import json
import time
import uuid
from pathlib import Path

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

    def __init__(self):

        self.client_id = str(uuid.uuid4())

    def _load_workflow(self):

        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate(
            self,
            prompt: str,
            output_name: str,
            negative_prompt: str = "",
            config: RenderConfig = DEV_RENDER,
    ):

        workflow = self._load_workflow()

        workflow[PROMPT_NODE]["inputs"]["text"] = prompt

        workflow[NEGATIVE_PROMPT_NODE]["inputs"]["text"] = negative_prompt

        workflow[SAMPLER_NODE]["inputs"]["steps"] = config.steps
        workflow[SAMPLER_NODE]["inputs"]["cfg"] = config.cfg
        workflow[SAMPLER_NODE]["inputs"]["seed"] = config.seed
        workflow[SAMPLER_NODE]["inputs"]["sampler_name"] = config.sampler
        workflow[SAMPLER_NODE]["inputs"]["scheduler"] = config.scheduler

        workflow[LATENT_NODE]["inputs"]["width"] = config.width
        workflow[LATENT_NODE]["inputs"]["height"] = config.height

        workflow[SAVE_NODE]["inputs"]["filename_prefix"] = output_name

        response = requests.post(

            f"{COMFY_URL}/prompt",

            json={

                "prompt": workflow,

                "client_id": self.client_id,

            },

        )

        response.raise_for_status()

        prompt_id = response.json()["prompt_id"]

        return self._wait(prompt_id)

    def _wait(self, prompt_id):

        while True:

            history = requests.get(

                f"{COMFY_URL}/history/{prompt_id}"

            ).json()

            if prompt_id in history:

                outputs = history[prompt_id]["outputs"]

                for node in outputs.values():

                    if "images" in node:
                        return node["images"]

            time.sleep(1)
