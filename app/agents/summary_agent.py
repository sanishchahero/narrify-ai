from app.domain.models.book import Book
from app.services.llm import LLMService


class SummaryAgent:
    def __init__(self):
        self.llm = LLMService()

    def summarize(self, book: Book) -> str:
        prompt = self.llm.load_prompt("summary")

        book_text = book.raw_text
        MAX_CHARS = 100_000  # ~20,000 words, rich for extracting core principles
        if len(book_text) > MAX_CHARS:
            chunk = MAX_CHARS // 3
            book_text = (
                book_text[:chunk]
                + "\n\n[... Key Chapters & Core Principles ...]\n\n"
                + book_text[len(book_text) // 2 - chunk // 2 : len(book_text) // 2 + chunk // 2]
                + "\n\n[... Key Lessons & Conclusion ...]\n\n"
                + book_text[-chunk:]
            )

        prompt += f"\n\nBOOK:\n{book_text}"

        return self.llm.generate(prompt)
