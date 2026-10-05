import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import requests

from app.config.comfy import (
    COMFY_URL,
    WORKFLOW_PATH,
    PROMPT_NODE,
    NEGATIVE_PROMPT_NODE,
    LATENT_NODE,
    SAMPLER_NODE,
    SAVE_NODE,
)
from app.config.render import RenderConfig, DEV_RENDER


class ComfyUIClient:

    def __init__(self, base_url: str = COMFY_URL):
        self.base_url = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())

    def _load_workflow(self) -> dict[str, Any]:
        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def is_connected(self) -> bool:
        """Check if ComfyUI server is reachable."""
        try:
            res = requests.get(f"{self.base_url}/system_stats", timeout=2)
            return res.status_code == 200
        except requests.RequestException:
            return False

    def generate(
        self,
        prompt: str,
        output_name: str,
        negative_prompt: str = "",
        config: RenderConfig = DEV_RENDER,
        seed: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        workflow = self._load_workflow()

        effective_seed = seed if seed is not None else config.seed

        workflow[PROMPT_NODE]["inputs"]["text"] = prompt
        workflow[NEGATIVE_PROMPT_NODE]["inputs"]["text"] = negative_prompt

        workflow[SAMPLER_NODE]["inputs"]["steps"] = config.steps
        workflow[SAMPLER_NODE]["inputs"]["cfg"] = config.cfg
        workflow[SAMPLER_NODE]["inputs"]["seed"] = effective_seed
        workflow[SAMPLER_NODE]["inputs"]["sampler_name"] = config.sampler
        workflow[SAMPLER_NODE]["inputs"]["scheduler"] = config.scheduler

        workflow[LATENT_NODE]["inputs"]["width"] = config.width
        workflow[LATENT_NODE]["inputs"]["height"] = config.height

        workflow[SAVE_NODE]["inputs"]["filename_prefix"] = output_name

        try:
            response = requests.post(
                f"{self.base_url}/prompt",
                json={
                    "prompt": workflow,
                    "client_id": self.client_id,
                },
                timeout=10,
            )
            response.raise_for_status()
            prompt_id = response.json()["prompt_id"]
            return self._wait(prompt_id)
        except requests.exceptions.ConnectionError as err:
            raise ConnectionError(
                f"Cannot connect to ComfyUI at {self.base_url}. Ensure ComfyUI is running via 'python main.py' in the ComfyUI directory."
            ) from err

    def get_image(
        self,
        filename: str,
        subfolder: str = "",
        folder_type: str = "output",
    ) -> bytes:
        """Retrieve raw image bytes from ComfyUI view endpoint."""
        response = requests.get(
            f"{self.base_url}/view",
            params={
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.content

    def _wait(self, prompt_id: str) -> list[dict[str, Any]]:
        while True:
            history_res = requests.get(f"{self.base_url}/history/{prompt_id}")
            history = history_res.json()

            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                for node in outputs.values():
                    if "images" in node:
                        return node["images"]

            time.sleep(1)
