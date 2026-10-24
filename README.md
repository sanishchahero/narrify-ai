# 📖 Narrify AI

> **Transform any book title or manuscript into viral, illustrated vertical videos (9:16) for TikTok, YouTube Shorts, and Instagram Reels — with zero manual downloads.**

Narrify AI combines cloud LLMs for high-context book research and narrative synthesis with local Stable Diffusion (ComfyUI on Apple Silicon Metal) for zero-cost AI illustration, voiceover narration, kinetic subtitles, and cinematic Ken Burns camera motion.

---

## ✨ Features

- 💡 **Instant Book-Title Input (Zero Downloads Needed)**: Simply type a book name (e.g. `"The Psychology of Money"`, `"Deep Work"`, `"Atomic Habits"`). Narrify AI automatically synthesizes a rich book knowledge dossier via LLM — or seamlessly uses your local PDF if provided!
- 🎬 **5-Act Viral Retention Engine**: Generates structured short-form scripts designed for high viewer retention:
  $$\text{Hook} \longrightarrow \text{Conventional Trap} \longrightarrow \text{Breakthrough Insight} \longrightarrow \text{Actionable Protocol} \longrightarrow \text{Triumphant Payoff}$$
- 🎨 **Anti-AI Plastic Illustration Engine**: Replaces generic, artificial corporate vector art with tactile, organic artistic mediums:
  * **`GROWTH_STORY`**: Growth Story Studio motion graphics aesthetic (isolated 3D isometric fintech icons, dark slate stage #0B0F19, split comparison cards [The Illusion vs The Reality], compounding curves, and translucent yellow highlighter callouts).
  * **`CINEMATIC`** (Default): 35mm film photography, Kodak Portra 400 grain, Leica 50mm f/1.4 lens, natural directional lighting, candid human expressions.
  * **`GHIBLI`**: Hand-painted Studio Ghibli gouache animation background, Kazuo Oga scenery, soft pastoral sunlight.
  * **`EDITORIAL`**: The New Yorker risograph print, limited palette (terracotta, cobalt, cream), matte paper grain, ligne claire line art.
  * **`VINTAGE_INK`**: Albrecht Dürer antique copperplate engraving, fine cross-hatched woodcut etching, aged parchment.
  * **`OIL_PAINTING`**: Classical impasto oil on canvas, textured palette knife strokes, Rembrandt chiaroscuro lighting.
  * **`WATERCOLOR`**: Translucent wet-on-wet washes on 300gsm cold-press Arches cotton paper with organic blooms.
  * **`HANDWRITTEN`**: Hand-drawn pen & ink sketch with delicate cross-hatching and warm sepia wash on ivory cream paper.
  * **`CARTOON`**: Whimsical hand-inked storybook cartoon with soft watercolor gouache fills (Calvin & Hobbes storybook aesthetic).
- 🚫 **Aggressive Anti-Artifact Filtering**: Custom negative prompt stack and LLM prompt filtering eliminate waxy plastic skin, 3D CGI sheen, barbie dolls, floating abstract icons, and split-screen clichés.
- 🎙️ **Ultra-Realistic Neural Voiceover**: Powered by high-fidelity Microsoft Edge Neural TTS voices (`christopher`, `guy`, `jenny`, `brian`, `ryan`, `aria`) with natural human breathing, cadence, and emotion — zero robotic speech!
- 🎵 **Ambient Background Music & Audio Ducking**: Automatically mixes and loops warm background music ducked underneath speech for broadcast-ready social media polish.
- 💬 **Kinetic Subtitles Without ImageMagick**: Generates high-contrast lower-third pill captions using Pillow with zero external dependencies.
- 🎥 **Cinematic 1080×1920 Export**: Stitches scenes, applies alternating Ken Burns camera zooms, syncs audio, and exports standard H.264/AAC vertical MP4.

---

## 🏗️ Architecture

```mermaid
flowchart LR
    A["📖 Book Title or PDF"] --> B["📚 BookLoader"]
    B -->|Local PDF| C["📖 PdfBookLoader"]
    B -->|Title Only| D["🌐 Book Research Agent (LLM)"]
    C & D --> E["🧠 SummaryAgent"]
    E --> F["🎬 ScriptAgent (5-Act Arc)"]
    F --> G["🎙️ TTSService (.mp3)"]
    F --> H["🎨 ComfyUI Diffusion (.png)"]
    F --> I["💬 SubtitleRenderer (PIL)"]
    G & H & I --> J["🎥 VideoComposer (MoviePy)"]
    J --> K["📱 Final MP4 (1080x1920)"]
```

---

## 🚀 Quickstart

### 1. Prerequisites
- **macOS** (Apple Silicon recommended for local Metal GPU acceleration) or Linux.
- **Python 3.11+**
- **[uv](https://github.com/astral-sh/uv)** (fast Python package manager):
  ```bash
  brew install uv
  ```

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/sanishchahero/narrify-ai.git
cd narrify-ai
uv venv
source .venv/bin/activate
uv sync
```

### 3. Environment Setup
Copy the example environment file and configure your OpenRouter API key:
```bash
cp .env.example .env
```

Ensure your `.env` contains:
```ini
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key-here
LLM_MODEL=meta-llama/llama-3.3-70b-instruct

IMAGE_PROVIDER=comfyui
IMAGE_MODEL=flux
COMFYUI_HOST=127.0.0.1
COMFYUI_PORT=8188
```

### 4. Launch Local ComfyUI
In a separate terminal, launch your local ComfyUI server:
```bash
cd ComfyUI
python main.py --listen 127.0.0.1 --port 8188
```
> **Note**: Ensure `DreamShaper_8_pruned.safetensors` is located in `ComfyUI/models/checkpoints/`.

---

## 💻 CLI Usage

### 🎥 1. Generate Full Vertical Video
Simply pass any book title (or a path to a PDF file):
```bash
# Just write the book title!
uv run python main.py "The Psychology of Money"

# Or explicitly using the video command:
uv run python main.py video "Atomic Habits"
```

**Options**:
- `--scenes`, `-n`: Number of scenes (default: `5`).
- `--style`, `-s`: Visual illustration aesthetic (`GROWTH_STORY`, `CINEMATIC`, `GHIBLI`, `EDITORIAL`, `VINTAGE_INK`, `OIL_PAINTING`, `WATERCOLOR`, `HANDWRITTEN`, `CARTOON`, `CHALKBOARD`). Default: `CINEMATIC`.
- `--voice`, `-v`: Narrator voice (`christopher`, `guy`, `jenny`, `brian`, `ryan`, `aria`, `eric`). Default: `christopher`.
- `--music`, `-m`: Custom background soundtrack MP3 (defaults to bundled ambient track).
- `--force`, `-f`: Force re-rendering of existing scene illustrations and audio.
- `--limit`: Render only the first $k$ scenes.

```bash
# Example: 35mm Cinematic film style with Christopher voice
uv run python main.py video "Deep Work" --style CINEMATIC --voice christopher -n 5

# Example: Studio Ghibli painterly aesthetic
uv run python main.py video "Atomic Habits" --style GHIBLI --voice jenny

# Example: New Yorker editorial risograph illustration
uv run python main.py video "The Psychology of Money" --style EDITORIAL --voice guy
```

### 📝 2. Preview Script & Book Summary
Preview the generated 5-act narrative script and core lessons without rendering images:
```bash
uv run python main.py summarize "The Psychology of Money"
```

### 🎨 3. Preview Diffusion Prompts
Inspect the enriched CLIP prompts generated for each scene:
```bash
uv run python main.py blueprint "Thinking, Fast and Slow" --style HANDWRITTEN
```

### 🖼️ 4. Render Illustrations Only
Generate only scene illustrations directly via ComfyUI:
```bash
uv run python main.py render-images "Atomic Habits"
```

---

## 🧪 Testing

Run the automated test suite with `pytest`:
```bash
uv run pytest
```

All 18 unit tests verify:
- BookLoader (Direct PDF, local folder fuzzy matching, and zero-download LLM research).
- OpenRouter LLM structured output and JSON schema adherence.
- CLIP token length constraints and prompt enhancer cleanliness.
- 5-scene viral narrative validation and error rejection.
- Pillow subtitle rendering and MoviePy video assembly.
- InfographicComposer 5-act Growth Story Studio motion graphic slide rendering.

---

## 📚 Technical Documentation

For an in-depth dive into the internal subsystems, pipeline mechanics, and performance benchmarks:
- [Technical Specification & Architecture](docs/TECHNICAL_DOCUMENTATION.md)
- [Growth Story Studio Graphics Architecture](docs/GROWTH_STORY_GRAPHICS_ARCHITECTURE.md)

---

## 📄 License

MIT License. See `LICENSE` for details.