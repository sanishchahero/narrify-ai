from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest

from app.domain.models.book import Book
from app.loaders.book_loader import BookLoader


def test_book_loader_direct_pdf():
    loader = BookLoader()
    with patch.object(loader.pdf_loader, "load") as mock_pdf_load:
        mock_pdf_load.return_value = Book(
            title="Atomic Habits", author="James Clear", pages=256, raw_text="Sample text"
        )
        # Use an existing pdf path
        result = loader.load("books/atomic_habits.pdf")
        assert result.title == "Atomic Habits"
        mock_pdf_load.assert_called_once_with("books/atomic_habits.pdf")


def test_book_loader_fuzzy_match_local_pdf():
    loader = BookLoader()
    with patch.object(loader.pdf_loader, "load") as mock_pdf_load:
        mock_pdf_load.return_value = Book(
            title="Atomic Habits", author="James Clear", pages=256, raw_text="Sample text"
        )
        result = loader.load("Atomic Habits")
        assert result.title == "Atomic Habits"
        mock_pdf_load.assert_called_once()


def test_book_loader_llm_research_when_no_pdf():
    loader = BookLoader()
    with patch.object(loader.llm, "generate") as mock_llm_gen:
        mock_llm_gen.return_value = (
            "The Psychology of Money by Morgan Housel\n\n"
            "Core Thesis: Doing well with money has a little to do with how smart you are and a lot to do with how you behave.\n"
            "Five principles: Compounding, Staying Wealthy, Freedom, Man in the Car Paradox, Reasonable > Rational."
        )

        result = loader.load("The Psychology of Money")
        assert result.author == "Morgan Housel"
        assert "Compounding" in result.raw_text
        assert result.pages == 0
