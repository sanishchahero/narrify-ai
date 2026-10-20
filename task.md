# Narrify AI — Roadmap & Optimization Backlog (`task.md`)

This document outlines the diagnosis of current limitations, architectural bottlenecks, and an actionable roadmap to elevate Narrify AI into a production-grade automated video generation engine.

---

## 🎯 Executive Diagnosis: Why Current Results Are Not Satisfactory

| Component | Current Implementation | Root Cause of Poor Quality |
| :--- | :--- | :--- |
| **PDF Ingestion & Context** | Flattens whole book into raw string; sends full text to local LLM | Local models (Ollama 8B) have limited context (`num_ctx` default ~2048-4096 tokens). **90%+ of the book is silently truncated**. The LLM only sees the preface/table of contents. |
| **Scriptwriting & Narrative** | Generic 3-line summary prompt fed into basic scriptwriter | Produces dry, clinical summaries lacking emotional hooks, narrative tension, relatable case studies, or pacing. |
| **Image Prompting (CLIP)** | Emits 150+ lines of markdown headers (`=== SCENE ===`, `Title:`) directly to ComfyUI | **Diffusion CLIP encoders cannot parse markdown metadata**. The 77-token CLIP window is completely consumed by headers and metadata before reaching visual descriptors. |
| **Visual Consistency** | Independent random generations with fixed seed (`seed: 42`) | Characters and environments change appearance completely between scenes. Hardcoded seed 42 also reduces visual variety where needed. |
| **ComfyUI Integration** | Workflow outputs are not downloaded back to local output directory | Generated images remain orphaned in ComfyUI's internal folder; `output/images/` stays empty. |
| **Model Incompatibilities** | Resolving 768x1344 on SD 1.5 checkpoints (`dreamshaper.json`) | SD 1.5 generates double torsos, duplicate limbs, and distorted faces when rendered at high vertical aspect ratios without hi-res fix or SDXL. |
| **Video Production** | Missing TTS, audio sync, subtitles, and video assembly | `moviepy` is imported but unused; no actual video (`.mp4`) is produced. |
| **Code Integrity** | Broken domain models (`video_blueprint` vs `storyboard`) | CLI commands (`blueprint`, `render-images`) and unit tests fail with `TypeError`. |

---

## 📋 Actionable Feature & Optimization Backlog

### Phase 1: Critical Bug Fixes & Code Consolidation (Immediate Stability)
- [x] **Unify Domain Models**:
  - Harmonized scene structures (`app/domain/models/scene.py` and `app/domain/models/video_blueprint.py`).
  - Fixed duplicate imports and missing Character references in `storyboard.py` and `scene.py`.
- [x] **Fix CLI Command Pipelines**:
  - Fixed argument signature mismatches in `main.py` (`blueprint`, `render-images`, `run`).
  - Added ComfyUI image retrieval: `ImageRenderer` now automatically downloads rendered `.png` files from ComfyUI `/view` endpoint directly to `output/images/`.
  - Added connection checking and scene-varied seed rendering.
- [x] **Repair Unit Test Suite**:
  - Rewrote `tests/test_prompt_enhancer.py` to cover both Blueprint and Storyboard scenes.
  - Added verification for prompt cleanliness (zero markdown headers or negative words in positive prompt).
  - All tests passing with `pytest`.

---

### Phase 2: High-Context Ingestion & Zero-Download Book Research
- [x] **Multi-Mode Book Ingestion (`BookLoader`)**:
  - Accept simple book title input (e.g. `"The Psychology of Money"`, `"Deep Work"`, `"Atomic Habits"`).
  - Automatically match local PDFs in `books/` by title if available.
  - Zero-download LLM book research: automatically synthesizes complete in-depth book dossiers (author, core thesis, 5 concepts, real stories, 3 actionable rules) when no local PDF is provided.
  - Retain direct PDF loading support via `PdfBookLoader`.
  - Added unit test suite in `tests/test_book_loader.py`.
- [x] **Cloud Open-Source LLM Integration (OpenRouter)**:
  - Added support for OpenRouter in `Settings` and `LLMService` without needing local Ollama.
  - Defaulted to open-source **`meta-llama/llama-3.3-70b-instruct`** with 128k context window support.
  - Added JSON schema enforcement & markdown code fence cleaning.
  - Preserved optional local Ollama fallback via `LLM_PROVIDER=ollama`.
  - Added unit test suite in `tests/test_llm_service.py`.

---

### Phase 3: Engaging Scriptwriting & Viral Pacing Engine
- [x] **High-Retention Narrative Frameworks**:
  - Implemented 5-act viral narrative structure (*Hook* $\rightarrow$ *Conventional Trap* $\rightarrow$ *Breakthrough Insight / Visual Metaphor* $\rightarrow$ *Actionable Protocol* $\rightarrow$ *Triumphant Payoff*).
  - Explicit scene constraints with concrete physical visual goals for AI diffusion generators.
  - Added `--scenes` / `-n` CLI flag to configure desired scene count (default 5 for 30–40s shorts).
- [x] **Pacing & Word-Per-Minute Calibration**:
  - Constrained narration to 1–2 punchy spoken sentences (15–25 words per scene) synced with TTS speech timing.
- [x] **Script Validation & Test Suite**:
  - Added `min_length=4` Pydantic validation on `ScriptResponse`.
  - Added unit test suite in `tests/test_script_agent.py` (13 tests passing).

---

### Phase 4: Diffusion Prompt Engineering & Image Quality Overhaul
- [x] **Re-engineer Prompt Synthesizer for CLIP**:
  - Removed all markdown keys, ASCII borders (`===`), narration transcripts, and dialogue from diffusion prompts.
  - Formatted prompts into dense, comma-separated tokens prioritizing Subject & Action in the first 25 tokens.
  - Integrated style presets (`HANDWRITTEN`, `CARTOON`, `CHALKBOARD`, `WATERCOLOR`) into clean positive descriptors.
- [x] **Optimized Negative Prompting**:
  - Cleaned up negative prompt to prevent mutated anatomy, deformed hands, duplicate subjects, and unwanted text/watermarks.
- [x] **Image Download & Dynamic Seed Management**:
  - Vary seed per scene (`config.seed + scene.id`) to avoid cloned compositions.
  - Automatically download and persist image binaries to `output/images/`.
- [x] **Checkpoint & Resolution Normalization**:
  - Configured `DreamShaper_8_pruned.safetensors` in `dreamshaper.json` and optimized `RenderConfig` for native 512x896 (9:16) rendering on Apple Silicon GPU (Metal Performance Shaders).
  - Reduced step time to ~1.3 seconds per iteration (~25s per scene render).

---

### Phase 5: Aesthetic & Character Consistency System
- [ ] **Visual Style Bible**:
  - Generate a single shared global aesthetic embedding / style prefix injected into every scene prompt.
  - Expand curated style presets: *Hand-drawn Ink & Watercolor*, *Vintage Lithograph*, *Minimalist Vector*, *Dark Academy Oil Painting*, *Claymation 3D*.
- [ ] **Character Consistency Pipeline**:
  - Maintain a persistent character descriptor (ethnicity, hair color/style, clothing, signature accessories).
  - Integrate ComfyUI **IP-Adapter** (Image Prompt Adapter) or **Reference-Only / ControlNet** to condition subsequent scenes on Scene 1 character portraits.
- [ ] **Image-to-Image / ControlNet Composition**:
  - Use ControlNet (Depth, Lineart, OpenPose) for complex postures and perspective consistency.

---

### Phase 6: Full Multimodal Video Assembly (The "Narrify" Engine)
- [x] **Ultra-Realistic Neural Voiceover (TTS)**:
  - Upgraded `TTSService` from legacy robotic `say` to state-of-the-art Microsoft Edge Neural TTS models (`edge-tts`).
  - Added curated storyteller personas: `christopher` (authoritative documentary), `guy` (passionate/viral), `jenny` (warm female), `ryan` (British), `brian` (conversational).
  - Preserved graceful offline fallback to local speech engines.
  - Zero API key required, sub-second duration sync.
- [x] **Ambient Background Music & Audio Ducking**:
  - Added ambient soundtrack mixing in `VideoComposer` with automatic looping and -22 dB (8% volume) ducking under speech.
  - Added `--music` / `-m` CLI option for custom background tracks.
- [x] **Automated Kinetic Subtitles / Captions**:
  - Built `SubtitleRenderer` using Pillow with high-contrast typography, text shadow, and translucent rounded pill backdrop.
  - Automatically wraps narration text to 1-3 lines centered in the lower-third.
- [x] **Motion & Camera Dynamics (Ken Burns Effects)**:
  - Built `VideoComposer` with alternating subtle zoom-in and zoom-out transitions (`vfx.Resize` + `vfx.Crop`) to keep static illustrations lively and cinematic.
- [x] **Full Video Assembly & Export**:
  - Stitches scenes, voiceover audio, background music, subtitles, and Ken Burns motion into vertical MP4 (1080x1920, H.264 / AAC, 30fps).
  - Added comprehensive test suite in `tests/test_video_pipeline.py`.

---

### Phase 7: Architecture, CLI & Interactive Review Workflow
- [ ] **LangGraph Orchestration Pipeline**:
  - Convert linear execution to a robust LangGraph state machine:
    `Ingest -> Extract Chapters -> Generate Script -> Review/Refine -> Build Storyboard -> Generate Audio -> Render Visuals -> Compose Video`.
- [ ] **CLI Polish & Rich Progress**:
  - Add Rich terminal status spinners, progress bars, and formatted script preview tables.
- [ ] **Interactive Web UI / Human-in-the-Loop (FastAPI + Modern Frontend)**:
  - Serve a lightweight review dashboard:
    - Preview generated script and edit scene narration before rendering.
    - Click-to-regenerate individual scene images with tweaked prompts.
    - Instant final video preview and download.
