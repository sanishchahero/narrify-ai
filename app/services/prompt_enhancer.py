import re
from typing import Any, Optional

from app.config.image_styles import ImageStyle, STYLE_PROMPTS


class PromptEnhancer:
    """
    Synthesizes dense, high-quality diffusion prompts optimized for CLIP text encoders.
    Produces prioritized comma-separated visual descriptions without markdown boilerplate
    or negative words in the positive prompt.
    """

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        # Remove markdown or label prefixes
        t = re.sub(r"^(?:visual prompt|visual goal|description):\s*", "", text, flags=re.IGNORECASE)
        # Remove abstract symbolism phrases that confuse diffusion models
        t = re.sub(r"\b(?:symbolizing|representing|signifying|as a symbol of)\s+[^,;.]*", "", t, flags=re.IGNORECASE)
        # Remove generic fluff words that induce plastic AI looks
        t = re.sub(r"\b(?:masterpiece|high quality|best quality|ultra detailed|photorealistic)\b", "", t, flags=re.IGNORECASE)
        # Clean extra commas and whitespace
        t = re.sub(r",\s*,+", ",", t)
        return t.strip().strip(",").strip()

    @staticmethod
    def enhance(
        scene: Any,
        context: Optional[Any] = None,
        style: ImageStyle = ImageStyle.CINEMATIC,
    ) -> str:
        prompt_parts: list[str] = []

        # 1. Base style keywords
        base_style = STYLE_PROMPTS.get(style, STYLE_PROMPTS[ImageStyle.CINEMATIC])

        # 2. Extract direct visual_prompt or visual_goal if present
        visual_prompt = getattr(scene, "visual_prompt", None)
        if visual_prompt:
            cleaned = PromptEnhancer._clean_text(str(visual_prompt))
            if cleaned:
                prompt_parts.append(cleaned)

        visual_goal = getattr(scene, "visual_goal", None)
        if visual_goal:
            cleaned = PromptEnhancer._clean_text(str(visual_goal))
            if cleaned:
                prompt_parts.append(cleaned)

        # 3. Extract from frame (Storyboard Scene)
        frame = getattr(scene, "frame", None)
        if frame:
            if getattr(frame, "primary_subject", None):
                subject_desc = getattr(frame, "subject_description", "")
                if subject_desc:
                    prompt_parts.append(f"{frame.primary_subject}, {subject_desc}")
                else:
                    prompt_parts.append(frame.primary_subject)

            if getattr(frame, "primary_action", None):
                prompt_parts.append(frame.primary_action)

            objects = getattr(frame, "important_objects", [])
            if objects:
                prompt_parts.append(f"featuring {', '.join(objects)}")

            fg = getattr(frame, "foreground", [])
            if fg:
                prompt_parts.append(f"foreground with {', '.join(fg)}")

            bg = getattr(frame, "background", [])
            if bg:
                prompt_parts.append(f"background with {', '.join(bg)}")

            metaphor = getattr(frame, "visual_metaphor", None)
            if metaphor and metaphor.lower() != "none":
                prompt_parts.append(f"visual metaphor of {metaphor}")

        # 4. Extract from blueprint Scene (subject, action, foreground, background)
        if hasattr(scene, "subject") and scene.subject:
            prompt_parts.append(str(scene.subject))
        if hasattr(scene, "action") and scene.action:
            prompt_parts.append(str(scene.action))
        if hasattr(scene, "foreground") and scene.foreground:
            prompt_parts.append(f"foreground with {scene.foreground}")
        if hasattr(scene, "background") and scene.background:
            prompt_parts.append(f"background with {scene.background}")

        # 5. Extract Characters
        characters = getattr(scene, "characters", [])
        if characters:
            char_descs = []
            for c in characters:
                if isinstance(c, str):
                    char_descs.append(c)
                else:
                    parts = []
                    gender = getattr(c, "gender", "")
                    age = getattr(c, "age", "")
                    if age or gender:
                        parts.append(f"{age} {gender}".strip())
                    if getattr(c, "hairstyle", None):
                        parts.append(str(c.hairstyle))
                    if getattr(c, "clothing", None):
                        parts.append(f"wearing {c.clothing}")
                    if parts:
                        char_descs.append(", ".join(parts))
            if char_descs:
                prompt_parts.append("; ".join(char_descs))

        # 6. Environment & Setting
        env = getattr(scene, "environment", None)
        if env:
            env_parts = []
            if getattr(env, "location", None):
                env_parts.append(str(env.location))
            if getattr(env, "time_of_day", None):
                env_parts.append(str(env.time_of_day))
            if getattr(env, "weather", None):
                env_parts.append(str(env.weather))
            if env_parts:
                prompt_parts.append(", ".join(env_parts))

        # 7. Camera & Composition
        cam = getattr(scene, "camera", None)
        if cam:
            if isinstance(cam, str):
                prompt_parts.append(f"{cam} camera angle")
            else:
                cam_parts = []
                if getattr(cam, "shot", None):
                    cam_parts.append(f"{cam.shot} shot")
                if getattr(cam, "angle", None):
                    cam_parts.append(f"{cam.angle} angle")
                if getattr(cam, "composition", None):
                    cam_parts.append(str(cam.composition))
                if cam_parts:
                    prompt_parts.append(", ".join(cam_parts))
        elif hasattr(scene, "composition") and scene.composition:
            prompt_parts.append(str(scene.composition))

        # 8. Lighting & Emotion
        if hasattr(scene, "lighting") and scene.lighting:
            prompt_parts.append(f"{scene.lighting} lighting")

        emotion = getattr(scene, "emotion", "")
        if emotion:
            prompt_parts.append(f"{emotion} mood")

        # 9. Visual Context / Global Style Rules
        if context:
            ctx_parts = []
            if getattr(context, "art_style", None):
                ctx_parts.append(str(context.art_style))
            if getattr(context, "illustration_style", None):
                ctx_parts.append(str(context.illustration_style))
            if getattr(context, "color_palette", None):
                ctx_parts.append(f"{context.color_palette} color palette")
            if getattr(context, "lighting_style", None):
                ctx_parts.append(f"{context.lighting_style} lighting")
            if getattr(context, "line_style", None):
                ctx_parts.append(f"{context.line_style} linework")
            if ctx_parts:
                prompt_parts.append(", ".join(ctx_parts))

        # 10. Append Base Style tokens
        prompt_parts.append(base_style)

        # Clean and join into single line comma-separated prompt
        cleaned_parts = [
            p.strip().rstrip(",")
            for p in prompt_parts
            if p and p.strip() and p.strip().lower() != "none"
        ]

        return ", ".join(cleaned_parts)
