from dataclasses import dataclass


@dataclass(slots=True)
class Chapter:
    number: int
    title: str
    content: str
