import textwrap
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


class SubtitleRenderer:
    """
    Renders stylish, high-retention vertical video subtitles (TikTok/Reels format)
    onto a transparent RGBA canvas using Pillow.
    """

    FONT_CANDIDATES = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial.ttf",
    ]

    def __init__(self, font_size: int = 54):
        self.font_size = font_size
        self.font = self._load_font(font_size)

    def _load_font(self, size: int) -> ImageFont.ImageFont:
        for font_path in self.FONT_CANDIDATES:
            if Path(font_path).exists():
                try:
                    return ImageFont.truetype(font_path, size=size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def render_overlay(
        self,
        text: str,
        video_size: Tuple[int, int] = (1080, 1920),
        y_percent: float = 0.78,
    ) -> Image.Image:
        """
        Creates a transparent (RGBA) image containing wrapped subtitles with a
        sleek dark pill background and crisp white text.
        """
        width, height = video_size
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Wrap text to max 28 characters per line
        wrapped_lines = textwrap.wrap(text, width=28)
        if not wrapped_lines:
            return overlay

        line_spacing = 16
        line_heights = []
        line_widths = []

        for line in wrapped_lines:
            bbox = draw.textbbox((0, 0), line, font=self.font)
            line_w = bbox[2] - bbox[0]
            line_h = bbox[3] - bbox[1]
            line_widths.append(line_w)
            line_heights.append(line_h)

        total_text_h = sum(line_heights) + line_spacing * (len(wrapped_lines) - 1)
        max_line_w = max(line_widths)

        # Padding for the backdrop pill
        pad_x = 36
        pad_y = 24
        pill_w = max_line_w + pad_x * 2
        pill_h = total_text_h + pad_y * 2

        center_x = width // 2
        center_y = int(height * y_percent)

        pill_box = [
            center_x - pill_w // 2,
            center_y - pill_h // 2,
            center_x + pill_w // 2,
            center_y + pill_h // 2,
        ]

        # Draw semi-transparent rounded rectangle (dark backdrop)
        draw.rounded_rectangle(
            pill_box,
            radius=24,
            fill=(10, 10, 15, 175),
            outline=(255, 255, 255, 60),
            width=2,
        )

        # Draw text lines centered inside the pill
        curr_y = center_y - total_text_h // 2
        for idx, line in enumerate(wrapped_lines):
            line_w = line_widths[idx]
            x = center_x - line_w // 2
            # Text shadow for maximum clarity
            draw.text((x + 2, curr_y + 2), line, font=self.font, fill=(0, 0, 0, 220))
            # Main white text
            draw.text((x, curr_y), line, font=self.font, fill=(255, 255, 255, 255))
            curr_y += line_heights[idx] + line_spacing

        return overlay
