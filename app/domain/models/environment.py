from dataclasses import dataclass, field


@dataclass(slots=True)
class Environment:
    location: str

    background: list[str]

    weather: str

    season: str

    time_of_day: str
