import fitz

from app.domain.models.book import Book
from app.services.text_cleaner import TextCleaner


class PdfBookLoader:

    def load(self, path: str) -> Book:

        document = fitz.open(path)

        pages = []

        for page in document:
            pages.append(page.get_text())

        raw_text = "\n".join(pages)

        raw_text = TextCleaner.clean(raw_text)

        return Book(
            title=document.metadata.get("title") or "Unknown",
            author=document.metadata.get("author") or "Unknown",
            pages=len(document),
            raw_text=raw_text,
        )