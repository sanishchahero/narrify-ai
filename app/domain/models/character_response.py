from pydantic import BaseModel, Field


class CharacterResponse(BaseModel):
    id: str

    name: str

    gender: str

    age: str

    hairstyle: str

    face: str

    clothing: str

    accessories: list[str] = Field(default_factory=list)