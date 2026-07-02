from dataclasses import dataclass, field

from .chapter import Chapter


@dataclass(slots=True)
class Book:
    title: str
    author: str
    pages: int
    raw_text: str
    chapters: list[Chapter] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return len(self.raw_text.split())
