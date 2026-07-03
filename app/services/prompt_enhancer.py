from app.config.image_styles import ImageStyle, STYLE_PROMPTS
from app.domain.models.scene import Scene
from app.domain.models.visual_context import VisualContext


class PromptEnhancer:

    @staticmethod
    def enhance(
        scene: Scene,
        context: VisualContext,
        style: ImageStyle = ImageStyle.HANDWRITTEN,
    ) -> str:

        base_style = STYLE_PROMPTS[style]

        characters = "\n".join(
            [
                f"""
Name: {c.name}
Gender: {c.gender}
Age: {c.age}
Hairstyle: {c.hairstyle}
Face: {c.face}
Clothing: {c.clothing}
Accessories: {", ".join(c.accessories) if c.accessories else "None"}
""".strip()
                for c in scene.characters
            ]
        )

        if not characters:
            characters = "No visible characters."

        objects = (
            ", ".join(scene.frame.important_objects)
            if scene.frame.important_objects
            else "None"
        )

        foreground = (
            ", ".join(scene.frame.foreground)
            if scene.frame.foreground
            else "None"
        )

        middle = (
            ", ".join(scene.frame.middle_ground)
            if scene.frame.middle_ground
            else "None"
        )

        background = (
            ", ".join(scene.frame.background)
            if scene.frame.background
            else "None"
        )

        secondary = (
            ", ".join(scene.frame.secondary_subjects)
            if scene.frame.secondary_subjects
            else "None"
        )

        metaphor = (
            scene.frame.visual_metaphor
            if scene.frame.visual_metaphor
            else "None"
        )

        return f"""
{base_style}

========================
SCENE
========================

Title:
{scene.title}

Narration:
{scene.narration}

Emotion:
{scene.emotion}

========================
PRIMARY SUBJECT
========================

{scene.frame.primary_subject}

Description:

{scene.frame.subject_description}

Primary Action:

{scene.frame.primary_action}

Secondary Subjects:

{secondary}

========================
CHARACTERS
========================

{characters}

========================
OBJECTS
========================

{objects}

Foreground:

{foreground}

Middle Ground:

{middle}

Background Elements:

{background}

========================
ENVIRONMENT
========================

Location:

{scene.environment.location}

Weather:

{scene.environment.weather}

Season:

{scene.environment.season}

Time:

{scene.environment.time_of_day}

========================
CAMERA
========================

Shot:

{scene.camera.shot}

Angle:

{scene.camera.angle}

Lens:

{scene.camera.lens}

Focus:

{scene.camera.focus}

Composition:

{scene.camera.composition}

========================
VISUAL STYLE
========================

Art Style:

{context.art_style}

Illustration Style:

{context.illustration_style}

Paper:

{context.paper_style}

Line Style:

{context.line_style}

Lighting:

{context.lighting_style}

Color Palette:

{context.color_palette}

Aspect Ratio:

{context.aspect_ratio}

========================
VISUAL METAPHOR
========================

{metaphor}

========================
IMPORTANT
========================

Create ONE educational illustration.

Everything must be clearly visible.

Use the listed objects.

Keep the same character appearance.

Hand-drawn educational notebook style.

Simple ink drawing.

Soft watercolor.

Vintage paper texture.

High detail.

No anime.

No manga.

No fantasy.

No random people.

No watermark.

No logo.

No text.

No speech bubbles.
""".strip()