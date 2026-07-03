from dataclasses import dataclass, field

from app.domain.models.camera import Camera
from app.domain.models.character import Character
from app.domain.models.environment import Environment

from dataclasses import dataclass, field

from app.domain.models.camera import Camera
from app.domain.models.environment import Environment
from app.domain.models.frame import Frame


@dataclass(slots=True)
class Scene:
    """
    One storyboard scene used throughout the rendering pipeline.
    """

    id: int

    title: str

    narration: str

    frame: Frame

    camera: Camera

    environment: Environment

    characters: list[str] = field(default_factory=list)

    emotion: str = ""

    music_mood: str = ""

    subtitle_style: str = ""

    sound_effects: list[str] = field(default_factory=list)