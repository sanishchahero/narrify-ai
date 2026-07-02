from pathlib import Path

from ollama import Client

from app.core.config import get_settings


class LLMService:
    def __init__(self):
        settings = get_settings()

        self.client = Client(host=settings.ollama_host)
        self.model = settings.llm_model

    def generate(self, prompt: str) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response["message"]["content"]

    @staticmethod
    def load_prompt(name: str) -> str:
        return Path(
            f"app/prompts/{name}.txt"
        ).read_text()