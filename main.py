from pathlib import Path

import typer

from app.loaders.pdf_loader import PdfBookLoader
from app.agents.summary_agent import SummaryAgent

app = typer.Typer()


@app.command()
def load(pdf: Path):
    loader = PdfBookLoader()

    book = loader.load(str(pdf))

    print(f"Title: {book.title}")
    print(f"Author: {book.author}")
    print(f"Pages: {book.pages}")
    print(f"Words: {book.word_count}")

@app.command()
def summarize(pdf: Path):

    loader = PdfBookLoader()

    book = loader.load(str(pdf))

    summary = SummaryAgent().summarize(book)

    print(summary)

if __name__ == "__main__":
    app()