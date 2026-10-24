import re
import sys
from pathlib import Path
from typing import Optional

import typer

from app.agents.script_agent import ScriptAgent
from app.agents.summary_agent import SummaryAgent
from app.config.image_styles import ImageStyle
from app.loaders.book_loader import BookLoader
from app.renderers.image_renderer import ImageRenderer
from app.services.prompt_enhancer import PromptEnhancer
from app.services.tts import TTSService
from app.services.video_composer import VideoComposer

app = typer.Typer(
    help="Narrify AI — Transform books into illustrated viral vertical videos.",
    no_args_is_help=True,
)


def _sanitize_title(title: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", title.lower().strip())
    clean = clean.strip("_")
    # Cap to safe 40 chars to prevent filesystem 'File name too long' errors
    return clean[:40].rstrip("_") or "book"


@app.command()
def video(
    book: str = typer.Argument(
        ...,
        help="Book title (e.g. 'Atomic Habits', 'The Psychology of Money') or path to PDF file",
    ),
    scenes: int = typer.Option(5, "--scenes", "-n", help="Target number of scenes (default 5 for 30-40s short)"),
    limit: Optional[int] = None,
    style: ImageStyle = typer.Option(ImageStyle.CINEMATIC, "--style", "-s", case_sensitive=False, help="Visual illustration style (growth_story, cinematic, ghibli, editorial, vintage_ink, oil_painting, watercolor, handwritten, cartoon, chalkboard)"),
    voice: str = typer.Option("christopher", "--voice", "-v", help="Narrator voice (christopher, guy, jenny, brian, eric, aria, ryan)"),
    music: Optional[Path] = typer.Option(None, "--music", "-m", help="Custom background soundtrack MP3 (defaults to ambient track)"),
    output: Path = Path("output"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-rendering of existing images and audio"),
):
    """
    Generate an end-to-end narrated video from a book name or PDF:
    1. Loads book (or researches knowledge dossier via LLM).
    2. Synthesizes a 5-act viral narrative script.
    3. Synthesizes voiceover narration with TTS.
    4. Renders AI scene illustrations via ComfyUI.
    5. Assembles final vertical MP4 with subtitles and Ken Burns motion.
    """
    loader = BookLoader()
    book_obj = loader.load(book)
    print(f"📖 Loaded '{book_obj.title}' by {book_obj.author} ({book_obj.word_count:,} words)")

    print(f"\n🧠 Generating {scenes}-scene video script via LLM...")
    summary = SummaryAgent().summarize(book_obj)
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
            "visual_goal": getattr(s, "visual_goal", ""),
            "image_path": img_file if img_file and img_file.exists() else None,
            "audio_path": audio_path,
            "duration": max(duration + 0.4, 2.5),
        })

    # 2. Final Video Assembly
    filename = _sanitize_title(book_obj.title)
    video_out = output / f"{filename}_video.mp4"
    print(f"\n🎥 Assembling final vertical video ({len(scenes_data)} scenes)...")
    composer = VideoComposer()
    composer.compose_video(
        scenes_data,
        video_out,
        bg_music_path=music,
        style=style,
        book_title=book_obj.title,
    )

    print("\n" + "=" * 80)
    print(f"🎉 FINAL VIDEO READY: {video_out}")
    print("=" * 80)


@app.command()
def summarize(
    book: str = typer.Argument(
        ...,
        help="Book title (e.g. 'Atomic Habits', 'The Psychology of Money') or path to PDF file",
    ),
    scenes: int = typer.Option(5, "--scenes", "-n", help="Target number of scenes (default 5 for 30-40s short)"),
):
    """Summarize a book and produce a 5-act viral video script preview."""
    loader = BookLoader()
    book_obj = loader.load(book)
    print(f"📖 Loaded: {book_obj.title} by {book_obj.author} ({book_obj.word_count:,} words)")

    print(f"\n🧠 Sending text to LLM for summary analysis...")
    summary = SummaryAgent().summarize(book_obj)
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
    book: str = typer.Argument(
        ...,
        help="Book title (e.g. 'Atomic Habits', 'The Psychology of Money') or path to PDF file",
    ),
    scenes: int = typer.Option(5, "--scenes", "-n", help="Target number of scenes"),
    style: ImageStyle = typer.Option(ImageStyle.CINEMATIC, "--style", "-s", case_sensitive=False, help="Visual illustration style (growth_story, cinematic, ghibli, editorial, vintage_ink, oil_painting, watercolor, handwritten, cartoon, chalkboard)"),
):
    """Generate diffusion-ready scene prompts for a book."""
    loader = BookLoader()
    book_obj = loader.load(book)
    print(f"📖 Loaded: {book_obj.title} by {book_obj.author}")

    summary = SummaryAgent().summarize(book_obj)
    script = ScriptAgent().generate(summary, target_scenes=scenes)

    print(f"\n✨ Generated Diffusion Prompts for {len(script.scenes)} scene(s):\n")
    for s in script.scenes:
        prompt = PromptEnhancer.enhance(s, style=style)
        print("=" * 80)
        print(f"SCENE {s.id} ({s.emotion})")
        print("=" * 80)
        print(f"Visual Goal: {s.visual_goal}")
        print(f"Prompt:      {prompt}")
        print()


@app.command()
def render_images(
    book: str = typer.Argument(
        ...,
        help="Book title (e.g. 'Atomic Habits', 'The Psychology of Money') or path to PDF file",
    ),
    scenes: int = typer.Option(5, "--scenes", "-n", help="Target number of scenes"),
    limit: Optional[int] = None,
    style: ImageStyle = typer.Option(ImageStyle.CINEMATIC, "--style", "-s", case_sensitive=False, help="Visual illustration style (growth_story, cinematic, ghibli, editorial, vintage_ink, oil_painting, watercolor, handwritten, cartoon, chalkboard)"),
    output: Path = Path("output"),
):
    """Generate script and render scene illustrations via ComfyUI."""
    loader = BookLoader()
    book_obj = loader.load(book)
    print(f"📖 Loaded: {book_obj.title} by {book_obj.author}")

    summary = SummaryAgent().summarize(book_obj)
    script = ScriptAgent().generate(summary, target_scenes=scenes)

    target_scenes = script.scenes[:limit] if limit else script.scenes

    renderer = ImageRenderer()
    image_dir = output / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🎨 Rendering {len(target_scenes)} scene illustrations via ComfyUI...")
    for s in target_scenes:
        img_file = image_dir / f"scene_{s.id:03}.png"
        print(f"  [Scene {s.id}] Rendering to {img_file}...")
        renderer.render_scene_image(scene=s, output_path=img_file, style=style)
        print(f"  💾 Saved: {img_file}")


def main_cli():
    # If a book title or file is provided as the first argument without a subcommand,
    # default directly to running 'video'
    known_commands = {"video", "summarize", "blueprint", "render-images", "--help", "-h"}
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in known_commands:
        sys.argv.insert(1, "video")
    app()


if __name__ == "__main__":
    main_cli()
