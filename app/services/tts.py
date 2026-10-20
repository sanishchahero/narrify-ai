import asyncio
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import imageio_ffmpeg
from moviepy import AudioFileClip

NEURAL_VOICE_MAP = {
    # Top Male Storytellers (Warm, authoritative, natural human cadence)
    "christopher": "en-US-ChristopherNeural",  # Deep, authoritative, documentary (Ideal for Non-fiction & Business)
    "guy": "en-US-GuyNeural",                  # Dynamic, energetic, passionate storyteller (Ideal for TikTok / Reels)
    "brian": "en-US-BrianNeural",              # Approachable, casual, modern conversational
    "eric": "en-US-EricNeural",                # Rational, crisp, modern YouTube explainer
    "ryan": "en-GB-RyanNeural",                # Refined British narrator (BBC / Documentary style)
    # Top Female Storytellers (Warm, expressive, natural breathing)
    "jenny": "en-US-JennyNeural",              # Warm, natural, friendly, expressive female
    "aria": "en-US-AriaNeural",                # Confident, clear, professional female
    "sonia": "en-GB-SoniaNeural",              # British female documentary voice
}

DEFAULT_NEURAL_VOICE = "en-US-ChristopherNeural"


class TTSService:
    """
    High-fidelity Text-To-Speech engine.
    Uses ultra-realistic Microsoft Edge Neural TTS voices by default,
    with automatic offline fallback to macOS 'say'.
    """

    def __init__(
        self,
        voice: str = "christopher",
        rate: str = "+0%",
        offline_rate: int = 175,
    ):
        self.voice = voice
        self.rate = rate
        self.offline_rate = offline_rate
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def resolve_voice(self, voice_input: str) -> str:
        clean = voice_input.lower().strip()
        if clean in NEURAL_VOICE_MAP:
            return NEURAL_VOICE_MAP[clean]
        if "neural" in clean:
            return voice_input
        # If user explicitly specifies a classic macOS voice (like Samantha or Daniel), check if neural default preferred
        if clean in ["samantha", "default"]:
            return DEFAULT_NEURAL_VOICE
        return voice_input

    def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None,
        rate: Optional[str] = None,
    ) -> Tuple[Path, float]:
        """
        Synthesize speech audio for the given text.
        Returns:
            Tuple[Path, float]: (path_to_audio_file, duration_seconds)
        """
        raw_voice = voice or self.voice
        resolved_voice = self.resolve_voice(raw_voice)
        effective_rate = rate or self.rate

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Attempt Neural TTS (High-fidelity human voice)
        if "neural" in resolved_voice.lower():
            try:
                self._synthesize_neural(text, resolved_voice, effective_rate, output_path)
                with AudioFileClip(str(output_path)) as audio_clip:
                    duration = float(audio_clip.duration)
                return output_path, duration
            except Exception as e:
                print(f"  ℹ️ Neural TTS unavailable ({e}), falling back to local speech engine...")

        # 2. Local Fallback (macOS 'say')
        return self._synthesize_macos(text, raw_voice, output_path)

    def _synthesize_neural(self, text: str, voice: str, rate: str, output_path: Path):
        import edge_tts

        rate_str = rate if str(rate).startswith(("+", "-")) else f"+{rate}%"

        async def _run():
            communicate = edge_tts.Communicate(text, voice=voice, rate=rate_str)
            await communicate.save(str(output_path))

        try:
            asyncio.run(_run())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_run())
            finally:
                loop.close()

    def _synthesize_macos(self, text: str, voice: str, output_path: Path) -> Tuple[Path, float]:
        say_bin = shutil.which("say")
        if not say_bin:
            raise RuntimeError("Speech synthesis failed: neither neural TTS nor macOS 'say' available.")

        mac_voice = voice if ("neural" not in voice.lower() and voice.lower() not in NEURAL_VOICE_MAP) else "Samantha"

        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp_aiff:
            tmp_aiff_path = Path(tmp_aiff.name)

        try:
            say_cmd = [
                say_bin,
                "-v", mac_voice,
                "-r", str(self.offline_rate),
                "-o", str(tmp_aiff_path),
                text,
            ]
            subprocess.run(say_cmd, check=True, capture_output=True)

            ffmpeg_cmd = [
                self.ffmpeg_exe,
                "-y",
                "-i", str(tmp_aiff_path),
                "-codec:a", "libmp3lame" if output_path.suffix == ".mp3" else "pcm_s16le",
                "-b:a", "192k",
                str(output_path),
            ]
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)

            with AudioFileClip(str(output_path)) as audio_clip:
                duration = float(audio_clip.duration)

            return output_path, duration
        finally:
            if tmp_aiff_path.exists():
                tmp_aiff_path.unlink()
