from pathlib import Path

from app.clients.comfyui_client import ComfyUIClient
from app.config.image_styles import ImageStyle
from app.config.render import DEV_RENDER, RenderConfig
from app.domain.models.storyboard import Storyboard
from app.services.prompt_enhancer import PromptEnhancer


NEGATIVE_PROMPT = """
anime,
manga,
waifu,
cartoon,
3d,
cgi,
photograph,
photorealistic,
low quality,
worst quality,
blurry,
text,
watermark,
logo,
signature,
extra arms,
extra legs,
extra fingers,
deformed,
bad anatomy,
duplicate people,
cropped,
oversaturated,
ugly
"""


class ImageRenderer:

    def __init__(
        self,
        config: RenderConfig = DEV_RENDER,
    ):
        self.client = ComfyUIClient()
        self.config = config

    def render(
        self,
        storyboard: Storyboard,
        output_dir: Path,
        limit: int | None = None,
    ):

        image_dir = output_dir / "images"
        image_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        scenes = storyboard.scenes

        if limit:
            scenes = scenes[:limit]

        total = len(scenes)

        print(f"\n🎨 Rendering {total} scene(s)...\n")

        for index, scene in enumerate(scenes, start=1):

            image_name = f"scene_{scene.id:03}"

            print(f"[{index}/{total}] {image_name}")

            prompt = PromptEnhancer.enhance(
                scene=scene,
                context=storyboard.visual_context,
                style=ImageStyle.HANDWRITTEN,
            )

            print("=" * 80)
            print(prompt)
            print("=" * 80)

            self.client.generate(
                prompt=prompt,
                negative_prompt=NEGATIVE_PROMPT,
                output_name=image_name,
                config=self.config,
            )

        print("\n✅ Image generation completed.\n")