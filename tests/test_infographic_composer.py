from pathlib import Path
from PIL import Image

from app.services.infographic_composer import InfographicComposer


def test_infographic_composer_renders_all_5_scenes():
    composer = InfographicComposer(target_size=(540, 960))

    # Test all 5 narrative scenes
    for scene_id in range(1, 6):
        img = composer.render_scene_slide(
            scene_id=scene_id,
            narration="Compounding is the eighth wonder of the world.",
            visual_goal="An isometric golden bank vault with an upward green compounding arrow.",
            book_title="THE PSYCHOLOGY OF MONEY",
        )
        assert isinstance(img, Image.Image)
        assert img.size == (540, 960)
        assert img.mode in ("RGB", "RGBA")
