from enum import Enum


class ImageStyle(str, Enum):
    HANDWRITTEN = "handwritten"
    CARTOON = "cartoon"
    CHALKBOARD = "chalkboard"
    WATERCOLOR = "watercolor"


STYLE_PROMPTS = {
    ImageStyle.HANDWRITTEN: """
Handwritten notebook illustration.

Black ink sketch.

Minimal watercolor wash.

Vintage cream paper.

Educational illustration.

Simple composition.

Soft shadows.

Consistent art style.

Vertical composition.

Aspect Ratio 9:16.

High quality.

No text.

No watermark.

No logo.

No signature.
""".strip(),

    ImageStyle.CARTOON: """
Cute educational cartoon.

Bright colors.

Simple characters.

Modern flat illustration.

Clean background.

Vertical composition.

Aspect Ratio 9:16.

High quality.

No text.

No watermark.
""".strip(),

    ImageStyle.CHALKBOARD: """
White chalk drawing.

Dark chalkboard background.

Hand drawn educational diagram.

Clean composition.

Minimal style.

Vertical composition.

Aspect Ratio 9:16.

High quality.

No watermark.
""".strip(),

    ImageStyle.WATERCOLOR: """
Beautiful watercolor painting.

Soft colors.

Minimal ink outlines.

Educational illustration.

Vertical composition.

Aspect Ratio 9:16.

High quality.

No watermark.
""".strip(),
}
