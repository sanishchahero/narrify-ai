from enum import Enum


class ImageStyle(str, Enum):
    HANDWRITTEN = "handwritten"
    CARTOON = "cartoon"
    CHALKBOARD = "chalkboard"
    WATERCOLOR = "watercolor"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
        return super()._missing_(value)


STYLE_PROMPTS = {
    ImageStyle.HANDWRITTEN: (
        "handwritten educational notebook sketch, clean black ink lineart, soft muted watercolor wash, "
        "vintage aged cream paper texture, minimalist editorial illustration, soft ambient lighting, "
        "vertical composition, 9:16 aspect ratio, masterpiece, highly detailed"
    ),
    ImageStyle.CARTOON: (
        "clean modern 2d vector cartoon, vibrant color palette, friendly aesthetic, charming character design, "
        "smooth flat illustration, clean composition, crisp outlines, vertical 9:16 framing, high quality"
    ),
    ImageStyle.CHALKBOARD: (
        "detailed white and colored chalk drawing on dark slate chalkboard, hand-drawn educational diagram, "
        "textured blackboard background, clean chalk lines, high contrast, vertical 9:16 composition"
    ),
    ImageStyle.WATERCOLOR: (
        "expressive watercolor painting, luminous translucent washes, delicate ink outlines, artistic paper texture, "
        "soft gradients, harmonious pastel color palette, vertical 9:16 portrait orientation, masterpiece"
    ),
}
