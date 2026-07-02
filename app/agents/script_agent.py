import json

from app.domain.models.script import Scene, VideoScript
from app.domain.models.script_response import ScriptResponse
from app.services.llm import LLMService


class ScriptAgent:
    def __init__(self):
        self.llm = LLMService()

    def generate(self, summary: str) -> VideoScript:

        prompt = self.llm.load_prompt("script_writer")

        prompt += f"\n\n{summary}"

        response = self.llm.generate(
            prompt,
            format="json",
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