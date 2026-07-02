from app.domain.models.book import Book
from app.services.llm import LLMService


class SummaryAgent:
    def __init__(self):
        self.llm = LLMService()

    def summarize(self, book: Book) -> str:
        prompt = self.llm.load_prompt("summary")

        prompt += f"\n\nBOOK:\n{book.raw_text}"

        return self.llm.generate(prompt)
