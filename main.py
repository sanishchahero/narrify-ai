from pathlib import Path
from typing import Optional

import typer

from app.agents.creative_director_agent import CreativeDirectorAgent
from app.agents.script_agent import ScriptAgent
from app.agents.storyboard_agent import StoryboardAgent
from app.agents.summary_agent import SummaryAgent
from app.config.image_styles import ImageStyle
from app.loaders.pdf_loader import PdfBookLoader
from app.renderers.image_renderer import ImageRenderer
from app.services.prompt_enhancer import PromptEnhancer
from app.services.subtitle_renderer import SubtitleRenderer
from app.services.tts import TTSService
from app.services.video_composer import VideoComposer

app = typer.Typer(help="Narrify AI - Turn books into illustrated video scripts and storyboards.")


@app.command()
def load(pdf: Path):
    """Inspect and extract metadata from a book PDF."""
    loader = PdfBookLoader()
    book = loader.load(str(pdf))

    print(f"Title: {book.title}")
    print(f"Author: {book.author}")
    print(f"Pages: {book.pages}")
    print(f"Words: {book.word_count}")


@app.command()
def summarize(
    pdf: Path,
    scenes: int = typer.Option(5, "--scenes", "-n", help="Target number of scenes (default 5 for 30-40s short)"),
):
    """Summarize a book and produce a preliminary video script."""
    print(f"📖 Loading PDF from '{pdf}'...")
    loader = PdfBookLoader()
    book = loader.load(str(pdf))
    print(f"✅ Loaded: {book.title} ({book.pages} pages, {book.word_count:,} words)")

    print(f"\n🧠 Sending text to LLM for summary analysis (this may take 30-60s for full books)...")
    summary = SummaryAgent().summarize(book)
    print("\n" + "=" * 80)
    print("📝 BOOK SUMMARY & CORE LESSONS")
    print("=" * 80)
    print(summary)
    print("=" * 80 + "\n")

    print(f"🎬 Crafting {scenes}-scene video script from summary...")
    script = ScriptAgent().generate(summary, target_scenes=scenes)

    print("\n" + "=" * 80)
    print(f"🎯 GENERATED VIDEO SCRIPT: {script.title}")
    print("=" * 80)
    print(f"🪝 Hook: {script.hook}\n")
    for scene in script.scenes:
        print(f"  [Scene {scene.id}] ({scene.duration}s | {scene.emotion}):")
        print(f"    Narration:   \"{scene.narration}\"")
        print(f"    Visual Goal: {scene.visual_goal}")
        print()
    print("=" * 80)


@app.command()
def blueprint(
    pdf: Path,
    style: ImageStyle = ImageStyle.HANDWRITTEN,
):
    """Generate a video blueprint with diffusion-ready scene prompts from a book."""
    print("📖 Loading book...")
    loader = PdfBookLoader()
    book = loader.load(str(pdf))
    print(f"✅ Loaded: {book.title}")

    print("🎬 Generating blueprint...")
    director = CreativeDirectorAgent()
    blueprint_data = director.run(book)

    print("\n✨ Generating Enhanced Diffusion Prompts:\n")
    for scene in blueprint_data.scenes:
        prompt = PromptEnhancer.enhance(
            scene,
            context=blueprint_data.visual_context,
            style=style,
        )

        print("=" * 80)
        print(f"SCENE {scene.id}: {scene.title}")
        print("=" * 80)
        print(prompt)
        print()


@app.command()
def render_images(
    pdf: Path,
    limit: Optional[int] = None,
    style: ImageStyle = ImageStyle.HANDWRITTEN,
    output: Path = Path("output"),
):
    """Generate blueprint and render scene images via ComfyUI."""
    loader = PdfBookLoader()
    book = loader.load(str(pdf))

    blueprint_data = CreativeDirectorAgent().run(book)

    print("=" * 80)
    print(f"Blueprint contains {len(blueprint_data.scenes)} scene(s)")
    print("=" * 80)

    for scene in blueprint_data.scenes:
        print(f"Scene {scene.id}: {scene.title}")

    renderer = ImageRenderer()
    renderer.render(
        blueprint_data,
        output,
        limit=limit,
        style=style,
    )


@app.command()
def run(
    pdf: Path,
    limit: Optional[int] = None,
    style: ImageStyle = ImageStyle.HANDWRITTEN,
    output: Path = Path("output"),
):
    """Execute complete storyboard pipeline and render illustrations."""
    loader = PdfBookLoader()
    book = loader.load(str(pdf))

    storyboard = StoryboardAgent().run(book)

    print("=" * 80)
    print(f"Storyboard contains {len(storyboard.scenes)} scene(s)")
    print("=" * 80)

    renderer = ImageRenderer()
    renderer.render(
        storyboard,
        output,
        limit=limit,
        style=style,
    )


@app.command()
def video(
    pdf: Path,
    scenes: int = typer.Option(5, "--scenes", "-n", help="Target number of scenes (default 5 for 30-40s short)"),
    limit: Optional[int] = None,
    style: ImageStyle = ImageStyle.HANDWRITTEN,
    voice: str = "Samantha",
    output: Path = Path("output"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-rendering of existing images and audio"),
):
    """
    Generate an end-to-end narrated video:
    1. Loads book and generates video script.
    2. Synthesizes voiceover narration with TTS.
    3. Renders AI scene illustrations via ComfyUI (or uses fallback title cards).
    4. Assembles final vertical MP4 with subtitles and Ken Burns motion.
    """
    loader = PdfBookLoader()
    book = loader.load(str(pdf))
    print(f"📖 Loaded '{book.title}' ({book.word_count:,} words)")

    print(f"\n🧠 Generating {scenes}-scene video script via LLM...")
    summary = SummaryAgent().summarize(book)
    script = ScriptAgent().generate(summary, target_scenes=scenes)

    script_scenes = script.scenes
    if limit:
        script_scenes = script_scenes[:limit]

    print(f"\n🎬 Script ready with {len(script_scenes)} scene(s).")
    print("=" * 80)
    print(f"Title: {script.title}")
    print(f"Hook:  {script.hook}")
    print("=" * 80)

    # 1. Image Generation & Voiceover Audio Synthesis
    tts = TTSService(voice=voice)
    renderer = ImageRenderer()
    audio_dir = output / "audio"
    image_dir = output / "images"

    scenes_data = []
    print("\n🎨 Generating scene illustrations & 🎙️ voiceover audio...")
    for s in script_scenes:
        # Audio synthesis
        audio_file = audio_dir / f"scene_{s.id:03}.mp3"
        if force or not audio_file.exists():
            audio_path, duration = tts.synthesize(s.narration, audio_file)
        else:
            audio_path, duration = tts.synthesize(s.narration, audio_file)

        # Image generation
        img_file = image_dir / f"scene_{s.id:03}.png"
        if force or not img_file.exists():
            print(f"  [Scene {s.id}] Rendering illustration via {renderer.image_provider.upper()} ({renderer.image_model})...")
            try:
                renderer.render_scene_image(
                    scene=s,
                    output_path=img_file,
                    style=style,
                )
                print(f"  💾 Image saved: {img_file}")
            except Exception as e:
                print(f"  ⚠️ Warning: Could not generate illustration for Scene {s.id}: {e}")
                img_file = None
        else:
            print(f"  [Scene {s.id}] Using existing image: {img_file}")

        print(f"  [Scene {s.id}] Narration: \"{s.narration}\" ({duration:.1f}s)\n")

        scenes_data.append({
            "id": s.id,
            "title": f"Scene {s.id}",
            "narration": s.narration,
            "image_path": img_file if img_file and img_file.exists() else None,
            "audio_path": audio_path,
            "duration": max(duration + 0.4, 2.5),
        })

    # 2. Final Video Assembly
    video_out = output / f"{pdf.stem}_video.mp4"
    print(f"\n🎥 Assembling final vertical video ({len(scenes_data)} scenes)...")
    composer = VideoComposer()
    composer.compose_video(scenes_data, video_out)

    print("\n" + "=" * 80)
    print(f"🎉 FINAL VIDEO READY: {video_out}")
    print("=" * 80)


if __name__ == "__main__":
    app()
