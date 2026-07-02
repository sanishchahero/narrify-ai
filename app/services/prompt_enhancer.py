from app.config.image_styles import (
    ImageStyle,
    STYLE_PROMPTS,
)
from app.domain.models.video_blueprint import Scene


class PromptEnhancer:

    @staticmethod
    def enhance(
            scene: Scene,
            style: ImageStyle = ImageStyle.HANDWRITTEN,
    ) -> str:
        style_prompt = STYLE_PROMPTS[style]

        return f"""
{style_prompt}

Scene Title

{scene.title}

Scene Description

{scene.visual_prompt}

Emotion

{scene.emotion}

Camera Movement

{scene.camera}

Instructions

Keep the artistic style identical to previous scenes.

Use the same colors, line thickness and composition style.

Do not add any text inside the illustration.

Illustration should be simple enough for educational videos.

Focus on one clear subject.

High detail.

Masterpiece quality.
""".strip()
