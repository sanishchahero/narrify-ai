import json
from typing import Optional

from app.domain.models.script import Scene, VideoScript
from app.domain.models.script_response import ScriptResponse
from app.services.llm import LLMService


class ScriptAgent:
    def __init__(self):
        self.llm = LLMService()

    def generate(self, summary: str, target_scenes: int = 5) -> VideoScript:
        prompt = self.llm.load_prompt("script_writer")
        prompt += f"\n\nTARGET NUMBER OF SCENES: {target_scenes}\n\nBOOK SUMMARY:\n{summary}"

        response = self.llm.generate(
            prompt,
            format="json",
            system_prompt=(
                f"You are an expert viral short-form video creator. You always return valid JSON "
                f"with exactly {target_scenes} scenes following the viral narrative arc."
            ),
        )

        data = ScriptResponse.model_validate(
            json.loads(response)
        )

        return VideoScript(
            title=data.title,
            hook=data.hook,
            summary=data.summary,
            scenes=[
                Scene(
                    id=s.id,
                    duration=s.duration,
                    narration=s.narration,
                    visual_goal=s.visual_goal,
                    emotion=s.emotion,
                )
                for s in data.scenes
            ],
        )