from dataclasses import dataclass


@dataclass(slots=True)
class Scene:
    id: int
    duration: int
    narration: str
    visual_goal: str
    emotion: str


@dataclass(slots=True)
class VideoScript:
    title: str
    hook: str
    summary: str
    scenes: list[Scene]
