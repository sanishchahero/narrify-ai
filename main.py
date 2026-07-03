from pathlib import Path

import typer
from pathlib import Path
from typing import Optional

from app.loaders.pdf_loader import PdfBookLoader
from app.agents.summary_agent import SummaryAgent
from app.agents.script_agent import ScriptAgent
from app.agents.creative_director_agent import CreativeDirectorAgent
from app.agents.storyboard_agent import StoryboardAgent

from app.services.prompt_enhancer import PromptEnhancer
from app.config.image_styles import ImageStyle
from app.renderers.image_renderer import ImageRenderer

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


@app.command()
def render_images(
        pdf: Path,
        limit: Optional[int] = None,
):
    loader = PdfBookLoader()

    book = loader.load(str(pdf))

    blueprint = CreativeDirectorAgent().run(book)

    print("=" * 80)
    print(f"Blueprint contains {len(blueprint.scenes)} scene(s)")
    print("=" * 80)

    for scene in blueprint.scenes:
        print(f"Scene {scene.id}: {scene.title}")

    renderer = ImageRenderer()

    renderer.render(
        blueprint,
        Path("output"),
        limit=limit,
    )

@app.command()
def run(pdf_path: str):
    loader = PdfBookLoader()

    book = loader.load(pdf_path)

    storyboard = StoryboardAgent().run(book)

    print("=" * 80)
    print(f"Storyboard contains {len(storyboard.scenes)} scenes")
    print("=" * 80)

    renderer = ImageRenderer()

    renderer.render(
        storyboard,
        Path("output"),
    )


if __name__ == "__main__":
    app()
