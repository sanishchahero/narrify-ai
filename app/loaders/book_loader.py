import os
import re
from pathlib import Path
from typing import Optional

from app.domain.models.book import Book
from app.loaders.pdf_loader import PdfBookLoader
from app.services.llm import LLMService


class BookLoader:
    """
    Intelligent Book Ingestion Engine:
    - If input is an existing PDF file path, loads it directly.
    - If input is a book title, checks 'books/' directory for a matching PDF.
    - If no local PDF exists, synthesizes a rich book knowledge dossier
      via LLM without requiring any manual PDF download.
    """

    def __init__(self):
        self.pdf_loader = PdfBookLoader()
        self.llm = LLMService()

    def load(self, book_input: str) -> Book:
        raw_path = Path(book_input)

        # 1. Direct file path check
        if raw_path.exists() and raw_path.is_file() and raw_path.suffix.lower() == ".pdf":
            print(f"📄 Found local PDF: {raw_path}")
            return self.pdf_loader.load(str(raw_path))

        # 2. Search local books/ folder for matching title
        books_dir = Path("books")
        if books_dir.exists():
            clean_input = re.sub(r"[^a-zA-Z0-9]", "", book_input.lower())
            for candidate in books_dir.glob("*.pdf"):
                clean_candidate = re.sub(r"[^a-zA-Z0-9]", "", candidate.stem.lower())
                if clean_input in clean_candidate or clean_candidate in clean_input:
                    print(f"📚 Matched local book in 'books/': {candidate.name}")
                    return self.pdf_loader.load(str(candidate))

        # 3. LLM-powered Book Knowledge Dossier (No download required!)
        print(f"🌐 No local PDF found. Researching '{book_input}' via knowledge base...")
        return self._research_book_dossier(book_input)

    def _research_book_dossier(self, book_title: str) -> Book:
        prompt = (
            f"You are a master book researcher and literary analyst.\n\n"
            f"Synthesize an in-depth, comprehensive dossier for the bestselling book:\n"
            f"\"{book_title}\"\n\n"
            f"Please structure your response with:\n"
            f"1. EXACT TITLE and AUTHOR\n"
            f"2. CORE THESIS: 1 comprehensive paragraph detailing the big idea.\n"
            f"3. FIVE CORE PRINCIPLES / MENTAL MODELS: In-depth breakdown of each concept.\n"
            f"4. CONCRETE CASE STUDIES & ANECDOTES: Real stories, scientific experiments, or historical events detailed in the book.\n"
            f"5. THREE ACTIONABLE PROTOCOLS: Step-by-step practical rules the reader can follow today.\n"
            f"6. VISUAL METAPHORS: Key analogies and physical metaphors used in the book."
        )

        dossier_text = self.llm.generate(
            prompt,
            system_prompt=(
                "You are an expert non-fiction book analyst. Provide rich, accurate, detailed "
                "summaries with real stories and key principles from the requested book."
            ),
        )

        # Extract title & author from first lines if possible
        author = "Unknown"
        title = book_title
        lines = [line.strip() for line in dossier_text.splitlines() if line.strip()]
        for line in lines[:5]:
            if "by " in line.lower():
                parts = re.split(r"by ", line, flags=re.IGNORECASE)
                if len(parts) == 2:
                    candidate_title = parts[0].strip().strip("*#\" ")
                    candidate_author = parts[1].strip().strip("*#\" ")
                    if 0 < len(candidate_title) < 60 and 0 < len(candidate_author) < 60:
                        title = candidate_title
                        author = candidate_author
                        break

        return Book(
            title=title,
            author=author,
            pages=0,
            raw_text=dossier_text,
        )
