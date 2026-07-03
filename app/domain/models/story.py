from dataclasses import dataclass


@dataclass(slots=True)
class Story:
    title: str

    hook: str

    scenes: list[str]

    ending: str
