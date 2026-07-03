from dataclasses import dataclass

from app.domain.models.scene import Scene
from app.domain.models.visual_context import VisualContext


@dataclass(slots=True)
class Storyboard:
    title: str

    hook: str

    ending: str

    visual_context: VisualContext

    character_bible: list[Character]

    scenes: list[Scene]
