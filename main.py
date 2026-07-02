from pathlib import Path

import typer

from app.loaders.pdf_loader import PdfBookLoader
from app.agents.summary_agent import SummaryAgent
from app.agents.script_agent import ScriptAgent
from app.agents.creative_director_agent import CreativeDirectorAgent
from app.services.prompt_enhancer import PromptEnhancer
from app.config.image_styles import ImageStyle

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

    script = ScriptAgent().generate(summary)

    print(script)


@app.command()
def blueprint(pdf: Path):
    """
    Generate a video blueprint from a book.
    """

    print("📖 Loading book...")

    loader = PdfBookLoader()
    book = loader.load(str(pdf))

    print(f"✅ Loaded: {book.title}")

    print("🎬 Generating blueprint...")

    director = CreativeDirectorAgent()

    blueprint = director.run(book)

    print("\nGenerating Enhanced Prompts\n")

    for scene in blueprint.scenes:
        prompt = PromptEnhancer.enhance(
            scene,
            style=ImageStyle.HANDWRITTEN,
        )

        print("=" * 80)
        print(f"SCENE {scene.id}")
        print("=" * 80)
        print(prompt)
        print()


if __name__ == "__main__":
    app()
