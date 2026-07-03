from pydantic import BaseModel, Field


class EnvironmentResponse(BaseModel):
    location: str

    background: list[str] = Field(default_factory=list)

    weather: str

    season: str

    time_of_day: str