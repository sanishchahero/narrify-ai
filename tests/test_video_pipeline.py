import tempfile
from pathlib import Path
import numpy as np

from app.services.subtitle_renderer import SubtitleRenderer
from app.services.tts import TTSService
from app.services.video_composer import VideoComposer


def test_subtitle_renderer():
    renderer = SubtitleRenderer()
    overlay = renderer.render_overlay(
        "Make it obvious, attractive, easy, and satisfying.",
        video_size=(540, 960),
    )
    assert overlay.size == (540, 960)
    assert overlay.mode == "RGBA"


def test_tts_service_synthesis():
    tts = TTSService()
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_mp3 = Path(tmp_dir) / "test_narration.mp3"
        audio_file, duration = tts.synthesize("Every habit starts small.", out_mp3)

        assert audio_file.exists()
        assert audio_file.stat().st_size > 0
        assert duration > 0.5


def test_video_composer_mock_scene():
    composer = VideoComposer(target_size=(360, 640), fps=15)
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_video = Path(tmp_dir) / "output.mp4"

        # Generate a brief audio
        tts = TTSService()
        audio_path, duration = tts.synthesize("Small steps win.", Path(tmp_dir) / "s1.mp3")

        scenes_data = [
            {
                "id": 1,
                "title": "Small Steps",
                "narration": "Small steps win.",
                "image_path": None,
                "audio_path": audio_path,
                "duration": duration + 0.3,
            }
        ]

        result = composer.compose_video(scenes_data, out_video)
        assert result.exists()
        assert result.stat().st_size > 1000
