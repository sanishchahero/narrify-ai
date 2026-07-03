from dataclasses import dataclass


@dataclass(slots=True)
class Camera:
    shot: str

    angle: str

    lens: str

    focus: str

    composition: str
