from enum import Enum


class ImageStyle(str, Enum):
    GROWTH_STORY = "growth_story"
    CINEMATIC = "cinematic"
    GHIBLI = "ghibli"
    EDITORIAL = "editorial"
    VINTAGE_INK = "vintage_ink"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    HANDWRITTEN = "handwritten"
    CARTOON = "cartoon"
    CHALKBOARD = "chalkboard"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            val_clean = value.lower().replace("-", "_").replace(" ", "_")
            for member in cls:
                if member.value == val_clean or member.name.lower() == val_clean:
                    return member
        return super()._missing_(value)


STYLE_PROMPTS = {
    ImageStyle.GROWTH_STORY: (
        "Growth Story Studio aesthetic, bright modern 2d editorial graphic illustration, "
        "clean crisp vector outlines, vibrant color palette with royal blue, warm gold, fresh emerald green and white, "
        "friendly and inspiring business storytelling, clear financial and psychological visual metaphor, "
        "modern digital explainer art, vertical 9:16"
    ),
    ImageStyle.CINEMATIC: (
        "candid 35mm film still photograph, Kodak Portra 400 grain, Leica 50mm f/1.4 lens, "
        "shallow depth of field, directional cinematic lighting, natural skin tones, "
        "tangible physical textures, subtle film imperfections, moody atmospheric grading, vertical 9:16"
    ),
    ImageStyle.GHIBLI: (
        "Studio Ghibli aesthetic, hand-painted gouache animation cel background, Kazuo Oga scenery, "
        "lush organic greenery, soft pastoral sunlight, artisanal brushstrokes, tranquil nostalgic atmosphere, "
        "traditional Japanese animation art, vertical 9:16"
    ),
    ImageStyle.EDITORIAL: (
        "minimalist editorial illustration, risograph print texture, limited color palette with warm terracotta, "
        "cobalt blue and cream, subtle ink misregistration, matte textured grain paper, ligne claire line art, "
        "The New Yorker graphic aesthetic, vertical 9:16"
    ),
    ImageStyle.VINTAGE_INK: (
        "Albrecht Durer copperplate engraving, antique cross-hatched woodcut etching, fine fountain pen lineart, "
        "monochrome sepia ink on aged parchment paper, 19th-century scientific plate, botanical illustration detail, vertical 9:16"
    ),
    ImageStyle.OIL_PAINTING: (
        "classical impasto oil painting on linen canvas, textured palette knife strokes, rich chiaroscuro lighting, "
        "Rembrandt amber and deep umber palette, visible canvas weave, museum fine art aesthetic, vertical 9:16"
    ),
    ImageStyle.WATERCOLOR: (
        "translucent wet-on-wet watercolor on cold-press 300gsm Arches cotton paper, natural pigment granulation, "
        "delicate graphite underdrawing, organic paint blooms and deckled edge texture, luminous wash, vertical 9:16"
    ),
    ImageStyle.HANDWRITTEN: (
        "hand-drawn ink and warm watercolor wash illustration, charming clear fountain pen lineart, "
        "bright sunny natural lighting, warm ivory art paper, friendly approachable character, "
        "clean artistic sketch, inspiring and educational aesthetic, vertical 9:16"
    ),
    ImageStyle.CARTOON: (
        "charming hand-drawn storybook cartoon illustration, cheerful friendly character, expressive hand-inked outlines, "
        "soft textured watercolor gouache paint, bright warm cozy lighting, gentle colorful pastel palette, "
        "handcrafted paper texture, vertical 9:16"
    ),
    ImageStyle.CHALKBOARD: (
        "hand-drawn chalk illustration on dark slate chalkboard, dusty white and muted pastel chalk strokes, "
        "authentic blackboard erased chalk dust texture, high contrast chiaroscuro, educational diagram aesthetic, vertical 9:16"
    ),
}
