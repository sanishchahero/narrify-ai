from pathlib import Path

from app.domain.models.video_blueprint import VideoBlueprint
from app.services.prompt_enhancer import PromptEnhancer


class PromptExporter:

    @staticmethod
    def export(
        blueprint: VideoBlueprint,
        output_dir: Path,
    ):

        prompt_dir = output_dir / "prompts"

        prompt_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for scene in blueprint.scenes:

            prompt = PromptEnhancer.enhance(scene)

            (prompt_dir / f"scene_{scene.id:03}.txt").write_text(
                prompt,
                encoding="utf-8",
            )