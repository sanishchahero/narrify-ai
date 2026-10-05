import json
import os
import re
from pathlib import Path
from typing import Any, Optional

import requests

from app.core.config import get_settings


def _clean_json_output(content: str) -> str:
    """Strip markdown code fence blocks if present."""
    content = content.strip()
    match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


class LLMService:
    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.llm_provider.lower()
        self.model = self.settings.llm_model

        if self.provider == "openrouter":
            self.api_key = self.settings.openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")
            self.base_url = self.settings.openrouter_base_url.rstrip("/")
        elif self.provider == "ollama":
            from ollama import Client
            self.client = Client(host=self.settings.ollama_host)
        else:
            raise ValueError(
                f"Unsupported LLM provider: '{self.provider}'. Supported: 'openrouter', 'ollama'."
            )

    def generate(
        self,
        prompt: str,
        format: Any | None = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate completion using OpenRouter or Ollama.
        Supports structured JSON output when format is provided.
        """
        if self.provider == "openrouter":
            return self._generate_openrouter(prompt, format=format, system_prompt=system_prompt)
        return self._generate_ollama(prompt, format=format)

    def _generate_openrouter(
        self,
        prompt: str,
        format: Any | None = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set. Please add your OpenRouter API key "
                "to the .env file (OPENROUTER_API_KEY=sk-or-v1-...) or set it as an environment variable."
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        user_content = prompt
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.settings.llm_temperature,
        }

        if format:
            # Instruct model to output JSON
            if isinstance(format, dict):
                user_content += (
                    f"\n\nIMPORTANT: You must return ONLY a valid JSON object matching this schema:\n"
                    f"{json.dumps(format, indent=2)}"
                )
            payload["response_format"] = {"type": "json_object"}

        messages.append({"role": "user", "content": user_content})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/narrify-ai",
            "X-Title": "Narrify AI",
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=180,
                )
                if response.status_code == 429 and attempt < max_retries - 1:
                    try:
                        err_data = response.json()
                        retry_after = int(err_data.get("metadata", {}).get("headers", {}).get("Retry-After", 10))
                    except Exception:
                        retry_after = 10
                    import time
                    print(f"⏳ OpenRouter admission control: waiting {retry_after}s before retry (attempt {attempt+1}/{max_retries})...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                if format:
                    content = _clean_json_output(content)
                return content
            except requests.HTTPError as err:
                error_msg = f"OpenRouter API request failed: {err}"
                try:
                    err_json = response.json()
                    if "error" in err_json:
                        error_msg += f" - Detail: {err_json['error']}"
                except Exception:
                    pass
                raise RuntimeError(error_msg) from err
        raise RuntimeError("OpenRouter API request failed after retries.")

    def _generate_ollama(
        self,
        prompt: str,
        format: Any | None = None,
    ) -> str:
        response = self.client.chat(
            model=self.model,
            format=format,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response["message"]["content"]
        if format:
            content = _clean_json_output(content)
        return content

    @staticmethod
    def load_prompt(name: str) -> str:
        return Path(f"app/prompts/{name}.txt").read_text(encoding="utf-8")
