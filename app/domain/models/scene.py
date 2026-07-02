from dataclasses import dataclass


@dataclass(slots=True)
class ScenePlan:
    id: int

    narration: str

    visual_prompt: str

    duration: float

    camera: str

    transition: str

    emotion: str

    subtitle_style: str

    sound_effects: list[str]