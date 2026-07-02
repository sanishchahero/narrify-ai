from dataclasses import dataclass, field


@dataclass(slots=True)
class Scene:
    id: int

    title: str

    narration: str

    visual_prompt: str

    duration: float

    camera: str

    transition: str

    subtitle_style: str

    emotion: str

    music_mood: str

    sound_effects: list[str] = field(default_factory=list)


@dataclass(slots=True)
class VideoBlueprint:
    title: str

    hook: str

    ending: str

    total_duration: float

    style: str

    scenes: list[Scene]