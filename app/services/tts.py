import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import imageio_ffmpeg
from moviepy import AudioFileClip


class TTSService:
    """
    Text-To-Speech engine.
    Uses macOS native high-quality speech synthesis ('say') converted via FFmpeg to mp3.
    """

    def __init__(self, voice: str = "Samantha", rate: int = 175):
        self.voice = voice
        self.rate = rate
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None,
        rate: Optional[int] = None,
    ) -> Tuple[Path, float]:
        """
        Synthesize speech audio for the given text.
        Returns:
            Tuple[Path, float]: (path_to_audio_file, duration_seconds)
        """
        effective_voice = voice or self.voice
        effective_rate = rate or self.rate

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if macOS 'say' command is available
        say_bin = shutil.which("say")
        if not say_bin:
            raise RuntimeError("macOS 'say' command not found. TTS requires a supported speech engine.")

        # Create temporary aiff file
        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp_aiff:
            tmp_aiff_path = Path(tmp_aiff.name)

        try:
            # 1. Synthesize audio with 'say'
            say_cmd = [
                say_bin,
                "-v", effective_voice,
                "-r", str(effective_rate),
                "-o", str(tmp_aiff_path),
                text,
            ]
            subprocess.run(say_cmd, check=True, capture_output=True)

            # 2. Convert to target format (.mp3 or .wav) using bundled FFmpeg
            ffmpeg_cmd = [
                self.ffmpeg_exe,
                "-y",
                "-i", str(tmp_aiff_path),
                "-codec:a", "libmp3lame" if output_path.suffix == ".mp3" else "pcm_s16le",
                "-b:a", "192k",
                str(output_path),
            ]
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)

            # 3. Determine duration
            with AudioFileClip(str(output_path)) as audio_clip:
                duration = float(audio_clip.duration)

            return output_path, duration

        finally:
            if tmp_aiff_path.exists():
                tmp_aiff_path.unlink()
