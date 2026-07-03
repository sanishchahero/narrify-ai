from dataclasses import dataclass, field


@dataclass(slots=True)
class VisualContext:
    art_style: str
    illustration_style: str
    color_palette: str
    paper_style: str
    line_style: str
    lighting_style: str
    aspect_ratio: str
