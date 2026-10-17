from dataclasses import dataclass, field


@dataclass(slots=True)
class Book:
    title: str
    author: str
    pages: int
    raw_text: str
    chapters: list[str] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return len(self.raw_text.split())
