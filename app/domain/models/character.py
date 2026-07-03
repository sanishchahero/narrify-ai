from dataclasses import dataclass


@dataclass(slots=True)
class Character:
    id: str

    name: str

    gender: str

    age: str

    hairstyle: str

    face: str

    clothing: str

    accessories: list[str]
