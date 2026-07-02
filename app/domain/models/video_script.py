from dataclasses import dataclass

from .scene import ScenePlan


@dataclass(slots=True)
class VideoScript:
    title: str
    hook: str
    summary: str

    scenes: list[ScenePlan]