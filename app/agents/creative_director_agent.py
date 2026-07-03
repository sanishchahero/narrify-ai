import json

from pydantic import ValidationError

from app.domain.models.book import Book
from app.domain.models.video_blueprint_response import VideoBlueprintResponse
from app.services.llm import LLMService
from app.domain.models.video_blueprint import (
    Scene,
    VideoBlueprint,
    VisualContext,
)


class CreativeDirectorAgent:
    MAX_RETRIES = 3

    def __init__(self):
        self.llm = LLMService()

    def run(self, book: Book) -> VideoBlueprint:

        prompt = (
            self.llm.load_prompt("creative_director")
            .replace("{{BOOK}}", book.raw_text)
        )

        for attempt in range(self.MAX_RETRIES):

            response = self.llm.generate(
                prompt,
                format=VideoBlueprintResponse.model_json_schema(),
            )

            try:

                blueprint = VideoBlueprintResponse.model_validate(

                    json.loads(response)
                )

                return self._to_domain(blueprint)

            except (ValidationError, json.JSONDecodeError):

                if attempt == self.MAX_RETRIES - 1:
                    raise RuntimeError(
                        "CreativeDirectorAgent failed to generate valid JSON."
                    )

        raise RuntimeError("Unexpected error.")

    @staticmethod
    def _to_domain(
            blueprint: VideoBlueprintResponse,
    ) -> VideoBlueprint:

        context = VisualContext(
            art_style=blueprint.visual_context.art_style,
            color_palette=blueprint.visual_context.color_palette,
            aspect_ratio=blueprint.visual_context.aspect_ratio,
            illustration_style=blueprint.visual_context.illustration_style,
            narrator_style=blueprint.visual_context.narrator_style,
            recurring_characters=blueprint.visual_context.recurring_characters,
        )

        scenes = []

        for scene in blueprint.scenes:
            scenes.append(
                Scene(
                    id=scene.id,
                    title=scene.title,
                    narration=scene.narration,
                    subject=scene.subject,
                    action=scene.action,
                    background=scene.background,
                    foreground=scene.foreground,
                    composition=scene.composition,
                    perspective=scene.perspective,
                    lighting=scene.lighting,
                    camera_motion=scene.camera_motion,
                    transition=scene.transition,
                    emotion=scene.emotion,
                    music_mood=scene.music_mood,
                    subtitle_style=scene.subtitle_style,
                    sound_effects=scene.sound_effects,
                )
            )

        return VideoBlueprint(
            title=blueprint.title,
            hook=blueprint.hook,
            ending=blueprint.ending,
            total_duration=0.0,
            visual_context=context,
            scenes=scenes,
        )
