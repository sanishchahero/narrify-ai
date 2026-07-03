import json

from pydantic import ValidationError

from app.domain.models.book import Book

from app.domain.models.storyboard import Storyboard
from app.domain.models.visual_context import VisualContext
from app.domain.models.character import Character
from app.domain.models.scene import Scene
from app.domain.models.frame import Frame
from app.domain.models.camera import Camera
from app.domain.models.environment import Environment

from app.domain.models.storyboard_response import StoryboardResponse

from app.services.llm import LLMService


class StoryboardAgent:
    MAX_RETRIES = 3

    def __init__(self):
        self.llm = LLMService()

    def run(self, book: Book) -> Storyboard:

        prompt = (
            self.llm.load_prompt("storyboard")
            .replace("{{BOOK}}", book.raw_text)
        )

        for attempt in range(self.MAX_RETRIES):

            response = self.llm.generate(
                prompt=prompt,
                format=StoryboardResponse.model_json_schema(),
            )

            try:

                storyboard = StoryboardResponse.model_validate(
                    json.loads(response)
                )

                return self._to_domain(storyboard)

            except (ValidationError, json.JSONDecodeError) as e:

                print(f"\nAttempt {attempt + 1} failed")
                print(e)

                if attempt == self.MAX_RETRIES - 1:
                    raise RuntimeError(
                        "StoryboardAgent failed to generate valid JSON."
                    )

        raise RuntimeError("Unexpected error.")

    @staticmethod
    def _to_domain(
        storyboard: StoryboardResponse,
    ) -> Storyboard:

        visual_context = VisualContext(
            art_style=storyboard.visual_context.art_style,
            illustration_style=storyboard.visual_context.illustration_style,
            color_palette=storyboard.visual_context.color_palette,
            paper_style=storyboard.visual_context.paper_style,
            line_style=storyboard.visual_context.line_style,
            lighting_style=storyboard.visual_context.lighting_style,
            aspect_ratio=storyboard.visual_context.aspect_ratio,
        )

        character_bible = []

        for c in storyboard.character_bible:

            character_bible.append(
                Character(
                    id=c.id,
                    name=c.name,
                    gender=c.gender,
                    age=c.age,
                    hairstyle=c.hairstyle,
                    face=c.face,
                    clothing=c.clothing,
                    accessories=c.accessories,
                )
            )

        scenes = []

        for scene in storyboard.scenes:

            frame = Frame(
                primary_subject=scene.frame.primary_subject,
                primary_action=scene.frame.primary_action,
                subject_description=scene.frame.subject_description,
                secondary_subjects=scene.frame.secondary_subjects,
                important_objects=scene.frame.important_objects,
                foreground=scene.frame.foreground,
                middle_ground=scene.frame.middle_ground,
                background=scene.frame.background,
                visual_metaphor=scene.frame.visual_metaphor,
            )

            camera = Camera(
                shot=scene.camera.shot,
                angle=scene.camera.angle,
                lens=scene.camera.lens,
                focus=scene.camera.focus,
                composition=scene.camera.composition,
            )

            environment = Environment(
                location=scene.environment.location,
                background=scene.environment.background,
                weather=scene.environment.weather,
                season=scene.environment.season,
                time_of_day=scene.environment.time_of_day,
            )

            characters = []

            for ch in scene.characters:

                characters.append(
                    Character(
                        id=ch.id,
                        name=ch.name,
                        gender=ch.gender,
                        age=ch.age,
                        hairstyle=ch.hairstyle,
                        face=ch.face,
                        clothing=ch.clothing,
                        accessories=ch.accessories,
                    )
                )

            scenes.append(
                Scene(
                    id=scene.id,
                    title=scene.title,
                    narration=scene.narration,
                    frame=frame,
                    camera=camera,
                    environment=environment,
                    characters=characters,
                    emotion=scene.emotion,
                    music_mood=scene.music_mood,
                    subtitle_style=scene.subtitle_style,
                    sound_effects=scene.sound_effects,
                )
            )

        return Storyboard(
            title=storyboard.title,
            hook=storyboard.hook,
            ending=storyboard.ending,
            visual_context=visual_context,
            character_bible=character_bible,
            scenes=scenes,
        )