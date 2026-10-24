import urllib.parse
from pathlib import Path
from typing import Any, Optional

import requests

from app.clients.comfyui_client import ComfyUIClient
from app.config.image_styles import ImageStyle
from app.config.render import DEV_RENDER, RenderConfig
from app.core.config import get_settings
from app.services.prompt_enhancer import PromptEnhancer

NEGATIVE_PROMPT = (
    "creepy, eerie, horror, grim, dark, gloomy, shadowy, pale face, scary, disturbing, "
    "haunted, ominous, misty, fog, hooded figure, sinister, weird expression, staring eyes, ghost, morbid, "
    "plastic skin, doll, barbie, airbrushed, wax, octane render, 3d render, cgi, unreal engine, "
    "smooth waxy skin, corporate vector, flat clipart, oversaturated, neon, stock photography, "
    "bad hands, deformed fingers, extra limbs, mutated anatomy, disfigured face, poorly drawn hands, "
    "duplicate subjects, blurry, low resolution, bad art, amateur, "
    "text, watermark, signature, logo, border, frame, collage, split screen, nsfw"
)

GROWTH_STORY_NEGATIVE_PROMPT = (
    "creepy, eerie, horror, grim, dark horror, ghostly, pale face, scary, disturbing, "
    "haunted, ominous, misty, fog, hooded figure, sinister, weird expression, staring eyes, ghost, morbid, "
    "photograph, realistic human face, portrait, cluttered background, room interior, scenic landscape, "
    "messy, classical painting, impasto, sketch, grunge, grainy, blurry, bad anatomy, "
    "extra limbs, deformed, watermark, signature, amateur, low resolution"
)


class ImageRenderer:

    def __init__(
        self,
        config: RenderConfig = DEV_RENDER,
    ):
        settings = get_settings()
        self.image_provider = getattr(settings, "image_provider", "cloud").lower()
        self.image_model = getattr(settings, "image_model", "flux").lower()
        self.config = config
        self.comfy_client = ComfyUIClient() if self.image_provider == "comfyui" else None

    def render_scene_image(
        self,
        scene: Any,
        output_path: Path,
        visual_context: Optional[Any] = None,
        style: ImageStyle = ImageStyle.CINEMATIC,
        seed: Optional[int] = None,
    ) -> Path:
        """
        Renders a single scene illustration to output_path using either
        cloud open-source FLUX or local ComfyUI.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        prompt = PromptEnhancer.enhance(
            scene=scene,
            context=visual_context,
            style=style,
        )

        effective_seed = seed if seed is not None else (self.config.seed + getattr(scene, "id", 1))

        if self.image_provider == "cloud":
            return self._render_cloud(prompt, output_path, effective_seed)
        else:
            return self._render_comfyui(prompt, output_path, effective_seed, style=style)

    def _render_cloud(
        self,
        prompt: str,
        output_path: Path,
        seed: int,
    ) -> Path:
        """Generates image using cloud open-source models with automatic retry and model fallback."""
        import time

        encoded_prompt = urllib.parse.quote(prompt)
        models_to_try = [self.image_model, "turbo", ""]

        for model in models_to_try:
            model_param = f"&model={model}" if model else ""
            url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width={self.config.width}&height={self.config.height}{model_param}&seed={seed}&nologo=true"
            )
            for attempt in range(2):
                try:
                    response = requests.get(url, timeout=60)
                    if response.status_code in (402, 429):
                        time.sleep(2)
                        continue
                    response.raise_for_status()
                    output_path.write_bytes(response.content)
                    return output_path
                except Exception:
                    time.sleep(1.5)

        raise RuntimeError(f"Cloud image generation failed for prompt: {prompt[:80]}...")

    def _render_comfyui(
        self,
        prompt: str,
        output_path: Path,
        seed: int,
        style: ImageStyle = ImageStyle.CINEMATIC,
    ) -> Path:
        """Generates image using local ComfyUI instance."""
        if not self.comfy_client or not self.comfy_client.is_connected():
            raise ConnectionError(
                "ComfyUI is not reachable at http://127.0.0.1:8188. "
                "Set IMAGE_PROVIDER=cloud in .env to use cloud FLUX without running ComfyUI."
            )

        neg = (
            GROWTH_STORY_NEGATIVE_PROMPT
            if style == ImageStyle.GROWTH_STORY
            else NEGATIVE_PROMPT
        )

        image_name = output_path.stem
        images = self.comfy_client.generate(
            prompt=prompt,
            negative_prompt=neg,
            output_name=image_name,
            config=self.config,
            seed=seed,
        )

        if not images:
            raise RuntimeError(f"No image returned from ComfyUI for {image_name}")

        first_img = images[0]
        img_bytes = self.comfy_client.get_image(
            filename=first_img["filename"],
            subfolder=first_img.get("subfolder", ""),
            folder_type=first_img.get("type", "output"),
        )
        output_path.write_bytes(img_bytes)
        return output_path

    def render(
        self,
        storyboard: Any,
        output_dir: Path,
        limit: Optional[int] = None,
        style: ImageStyle = ImageStyle.CINEMATIC,
    ) -> list[Path]:
        """
        Renders all scenes from a Storyboard or VideoBlueprint into output_dir / 'images'.
        """
        image_dir = output_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)

        scenes = getattr(storyboard, "scenes", [])
        if limit:
            scenes = scenes[:limit]

        total = len(scenes)
        print(f"\n🎨 Rendering {total} scene illustration(s) via {self.image_provider.upper()} ({self.image_model})...\n")

        saved_files: list[Path] = []
        visual_context = getattr(storyboard, "visual_context", None)

        for index, scene in enumerate(scenes, start=1):
            image_name = f"scene_{scene.id:03}.png"
            dest_file = image_dir / image_name
            print(f"[{index}/{total}] Generating illustration for Scene {scene.id}...")

            try:
                self.render_scene_image(
                    scene=scene,
                    output_path=dest_file,
                    visual_context=visual_context,
                    style=style,
                    seed=self.config.seed + scene.id,
                )
                saved_files.append(dest_file)
                print(f"  💾 Saved to {dest_file}")
            except Exception as e:
                print(f"  ❌ Error generating {image_name}: {e}")

        print(f"\n✅ Image generation completed. {len(saved_files)} file(s) saved in {image_dir}.\n")
        return saved_files