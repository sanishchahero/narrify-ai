import math
from pathlib import Path
from typing import Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from app.config.image_styles import ImageStyle


class InfographicComposer:
    """
    Renders 1080x1920 motion graphic explainer slides replicating the exact visual
    grammar of YouTube channels like Growth Story Studio, Vox, and Finshots:
      1. Deep dark slate canvas (#0B0F19 to #161E2E) with subtle grid & radial glow.
      2. Category tag pill at top ([ MONEY PSYCHOLOGY · LESSON X ]).
      3. Bold, high-contrast typography headlines.
      4. Dynamic content cards:
         - Scene 1: Pattern Interrupt Hook & Hero 3D Asset
         - Scene 2: Split Comparison Cards (The Illusion [Red] vs The Reality [Green])
         - Scene 3: Compounding Growth & Mathematical Mechanism
         - Scene 4: Document Rule & Translucent Highlighter Callout
         - Scene 5: Triumphant Freedom Equation & Payoff Badge
    """

    FONT_BOLD_CANDIDATES = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]

    FONT_REG_CANDIDATES = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]

    def __init__(self, target_size: Tuple[int, int] = (1080, 1920)):
        self.width, self.height = target_size
        self.base_width, self.base_height = 1080, 1920
        self._font_bold_path = self._find_font(self.FONT_BOLD_CANDIDATES)
        self._font_reg_path = self._find_font(self.FONT_REG_CANDIDATES)

    def _find_font(self, candidates: list[str]) -> Optional[str]:
        for path_str in candidates:
            if Path(path_str).exists():
                return path_str
        return None

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.ImageFont:
        font_path = self._font_bold_path if bold else self._font_reg_path
        if font_path:
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception:
                pass
        return ImageFont.load_default()

    def _draw_base_stage(
        self,
        glow_color: Tuple[int, int, int] = (0, 230, 118),
        glow_cy: int = 800,
        glow_radius: int = 450,
    ) -> Image.Image:
        """Draws the dark slate background (#0B0F19) with a subtle grid and ambient radial glow."""
        w, h = self.base_width, self.base_height
        canvas = Image.new("RGBA", (w, h), (11, 15, 25, 255))
        draw = ImageDraw.Draw(canvas)

        # Subtle dark slate grid (60px)
        grid_spacing = 60
        for x in range(0, w, grid_spacing):
            draw.line([(x, 0), (x, h)], fill=(30, 41, 59, 100), width=1)
        for y in range(0, h, grid_spacing):
            draw.line([(0, y), (w, y)], fill=(30, 41, 59, 100), width=1)

        # Ambient radial glow
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        cx = w // 2
        r_r, r_g, r_b = glow_color
        for r in range(glow_radius, 0, -18):
            alpha = int(22 * (1 - r / glow_radius))
            glow_draw.ellipse(
                [cx - r, glow_cy - r, cx + r, glow_cy + r],
                fill=(r_r, r_g, r_b, alpha),
            )
        return Image.alpha_composite(canvas, glow)

    def _draw_pill_badge(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        y: int = 160,
        accent_color: Tuple[int, int, int] = (0, 230, 118),
    ) -> None:
        """Draws a sleek category pill with an accent pulse dot."""
        font_tag = self._get_font(26, bold=True)
        t_bbox = draw.textbbox((0, 0), text, font=font_tag)
        tw = t_bbox[2] - t_bbox[0]
        th = t_bbox[3] - t_bbox[1]
        px, py = 28, 12
        pill_w = tw + px * 2 + 28
        pill_h = th + py * 2
        pill_x = (self.base_width - pill_w) // 2

        draw.rounded_rectangle(
            [pill_x, y, pill_x + pill_w, y + pill_h],
            radius=pill_h // 2,
            fill=(19, 29, 45, 230),
            outline=(*accent_color, 180),
            width=2,
        )
        # Pulse dot
        dot_r = 5
        draw.ellipse(
            [pill_x + 20, y + pill_h // 2 - dot_r, pill_x + 20 + dot_r * 2, y + pill_h // 2 + dot_r],
            fill=accent_color,
        )
        draw.text((pill_x + px + 12, y + py), text, font=font_tag, fill=accent_color)

    def render_scene_slide(
        self,
        scene_id: int,
        narration: str,
        visual_goal: str = "",
        book_title: str = "THE PSYCHOLOGY OF MONEY",
        hero_image_path: Optional[Path] = None,
        total_scenes: int = 5,
    ) -> Image.Image:
        """
        Renders an authentic, complete 1080x1920 Growth Story Studio motion graphic frame
        tailored to the 5-act narrative role of the scene.
        """
        clean_book = book_title.upper().replace("_", " ")

        if scene_id == 1:
            slide = self._render_scene_1_hook(narration, clean_book, hero_image_path)
        elif scene_id == 2:
            slide = self._render_scene_2_trap(narration, clean_book, hero_image_path)
        elif scene_id == 3:
            slide = self._render_scene_3_breakthrough(narration, clean_book, hero_image_path)
        elif scene_id == 4:
            slide = self._render_scene_4_rule(narration, clean_book, hero_image_path)
        else:
            slide = self._render_scene_5_payoff(narration, clean_book, hero_image_path)

        if (self.width, self.height) != (self.base_width, self.base_height):
            slide = slide.resize((self.width, self.height), Image.Resampling.LANCZOS)

        return slide

    def _render_scene_1_hook(
        self, narration: str, book: str, hero_image_path: Optional[Path]
    ) -> Image.Image:
        """Scene 1: The Hook & Pattern Interrupt."""
        img = self._draw_base_stage(glow_color=(0, 230, 118), glow_cy=850)
        draw = ImageDraw.Draw(img)

        # 1. Pill
        self._draw_pill_badge(draw, f"{book}  ·  THE HOOK", y=150, accent_color=(0, 230, 118))

        # 2. Main Headline
        font_hl = self._get_font(60, bold=True)
        font_sub = self._get_font(34, bold=False)

        h1 = "THE BIGGEST WEALTH TRAP"
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), h1, font=font_hl)[2]) // 2, 280),
            h1,
            font=font_hl,
            fill=(255, 255, 255),
        )

        h2 = "Behavior Matters More Than Intelligence"
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), h2, font=font_sub)[2]) // 2, 360),
            h2,
            font=font_sub,
            fill=(0, 230, 118),
        )

        # 3. Hero Visual Asset Frame (Upper Center)
        frame_w, frame_h = 760, 800
        frame_x = (self.base_width - frame_w) // 2
        frame_y = 440

        # Background card for hero image
        draw.rounded_rectangle(
            [frame_x, frame_y, frame_x + frame_w, frame_y + frame_h],
            radius=32,
            fill=(20, 27, 40, 240),
            outline=(0, 230, 118, 160),
            width=2,
        )

        # Embed hero image if present
        if hero_image_path and Path(hero_image_path).exists():
            try:
                hero_raw = Image.open(hero_image_path).convert("RGBA")
                # Resize keeping aspect
                scale = min((frame_w - 40) / hero_raw.width, (frame_h - 40) / hero_raw.height)
                nw = int(hero_raw.width * scale)
                nh = int(hero_raw.height * scale)
                hero_resized = hero_raw.resize((nw, nh), Image.Resampling.LANCZOS)
                ix = frame_x + (frame_w - nw) // 2
                iy = frame_y + (frame_h - nh) // 2
                img.paste(hero_resized, (ix, iy), hero_resized)
                draw = ImageDraw.Draw(img)
            except Exception:
                pass

        # 4. Stat Pill Callout at bottom of hero
        stat_w, stat_h = 680, 120
        stat_x = (self.base_width - stat_w) // 2
        stat_y = 1300
        draw.rounded_rectangle(
            [stat_x, stat_y, stat_x + stat_w, stat_y + stat_h],
            radius=20,
            fill=(17, 24, 39, 240),
            outline=(255, 215, 0, 180),
            width=2,
        )
        font_stat = self._get_font(36, bold=True)
        s_text = "FINANCIAL SUCCESS = 80% BEHAVIOR, 20% HEAD KNOWLEDGE"
        lines = [
            "FINANCIAL SUCCESS =",
            "80% BEHAVIOR  ·  20% HEAD KNOWLEDGE",
        ]
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), lines[0], font=self._get_font(26, bold=False))[2]) // 2, stat_y + 22),
            lines[0],
            font=self._get_font(26, bold=False),
            fill=(148, 163, 184),
        )
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), lines[1], font=font_stat)[2]) // 2, stat_y + 58),
            lines[1],
            font=font_stat,
            fill=(255, 215, 0),
        )

        return img

    def _render_scene_2_trap(
        self, narration: str, book: str, hero_image_path: Optional[Path]
    ) -> Image.Image:
        """Scene 2: The Conventional Trap / Split Comparison Cards."""
        img = self._draw_base_stage(glow_color=(255, 82, 82), glow_cy=900)
        draw = ImageDraw.Draw(img)

        # 1. Pill
        self._draw_pill_badge(draw, f"{book}  ·  THE TRAP", y=150, accent_color=(255, 82, 82))

        # 2. Headline
        font_hl = self._get_font(60, bold=True)
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), "THE STATUS ILLUSION", font=font_hl)[2]) // 2, 270),
            "THE STATUS ILLUSION",
            font=font_hl,
            fill=(255, 255, 255),
        )

        # 3. Two Comparison Cards Side-by-Side
        card_w = 450
        card_h = 740
        card_y = 400

        # Left Card (The Illusion - Red Trap)
        c1_x = 65
        draw.rounded_rectangle(
            [c1_x, card_y, c1_x + card_w, card_y + card_h],
            radius=28,
            fill=(23, 27, 38, 240),
            outline=(255, 82, 82, 180),
            width=2,
        )
        draw.rounded_rectangle([c1_x + 20, card_y + 20, c1_x + card_w - 20, card_y + 76], radius=14, fill=(48, 20, 28))
        draw.text((c1_x + 35, card_y + 32), "THE ILLUSION ✖", font=self._get_font(34, bold=True), fill=(255, 82, 82))

        rows_left = [
            ("Monthly Income", "₹1,50,000", (226, 232, 240)),
            ("Car & Phone EMI", "₹85,000 / mo", (255, 99, 132)),
            ("Status Display", "High Ego / Luxury", (148, 163, 184)),
            ("True Savings", "₹5,000 / mo", (255, 99, 132)),
            ("10-Year Wealth", "₹0 (DEBT TRAP)", (255, 82, 82)),
        ]
        ry = card_y + 115
        for label, val, color in rows_left:
            draw.text((c1_x + 30, ry), label.upper(), font=self._get_font(22, bold=False), fill=(148, 163, 184))
            draw.text((c1_x + 30, ry + 30), val, font=self._get_font(28, bold=True), fill=color)
            draw.line([(c1_x + 25, ry + 78), (c1_x + card_w - 25, ry + 78)], fill=(40, 48, 66), width=1)
            ry += 105

        # Right Card (The Reality - Green Wealth)
        c2_x = 565
        draw.rounded_rectangle(
            [c2_x, card_y, c2_x + card_w, card_y + card_h],
            radius=28,
            fill=(23, 27, 38, 240),
            outline=(0, 230, 118, 180),
            width=2,
        )
        draw.rounded_rectangle([c2_x + 20, card_y + 20, c2_x + card_w - 20, card_y + 76], radius=14, fill=(16, 45, 30))
        draw.text((c2_x + 35, card_y + 32), "THE REALITY ✔", font=self._get_font(34, bold=True), fill=(0, 230, 118))

        rows_right = [
            ("Monthly Income", "₹1,50,000", (226, 232, 240)),
            ("Living Expenses", "₹45,000 / mo", (0, 230, 118)),
            ("Compounding SIP", "₹75,000 / mo", (255, 215, 0)),
            ("Status Display", "Zero Ego / Low Profile", (148, 163, 184)),
            ("10-Year Wealth", "₹2.14 CRORE", (0, 230, 118)),
        ]
        ry = card_y + 115
        for label, val, color in rows_right:
            draw.text((c2_x + 30, ry), label.upper(), font=self._get_font(22, bold=False), fill=(148, 163, 184))
            draw.text((c2_x + 30, ry + 30), val, font=self._get_font(28, bold=True), fill=color)
            draw.line([(c2_x + 25, ry + 78), (c2_x + card_w - 25, ry + 78)], fill=(40, 48, 66), width=1)
            ry += 105

        # 4. Bottom Rule Callout
        box_w, box_h = 950, 140
        box_x = (self.base_width - box_w) // 2
        box_y = 1200
        draw.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=20,
            fill=(17, 24, 39, 230),
            outline=(255, 215, 0, 160),
            width=2,
        )
        draw.text((box_x + 40, box_y + 28), "THE GOLDEN INSIGHT:", font=self._get_font(24, bold=True), fill=(255, 215, 0))
        q = '"Rich is what you spend. Wealth is what you don\'t see."'
        draw.text((box_x + 40, box_y + 70), q, font=self._get_font(30, bold=False), fill=(255, 255, 255))

        return img

    def _render_scene_3_breakthrough(
        self, narration: str, book: str, hero_image_path: Optional[Path]
    ) -> Image.Image:
        """Scene 3: The Compounding Breakthrough Mechanism."""
        img = self._draw_base_stage(glow_color=(0, 230, 118), glow_cy=850)
        draw = ImageDraw.Draw(img)

        # 1. Pill
        self._draw_pill_badge(draw, f"{book}  ·  THE BREAKTHROUGH", y=150, accent_color=(0, 230, 118))

        # 2. Headline
        font_hl = self._get_font(60, bold=True)
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), "THE LAW OF COMPOUNDING", font=font_hl)[2]) // 2, 270),
            "THE LAW OF COMPOUNDING",
            font=font_hl,
            fill=(255, 255, 255),
        )

        # 3. Compounding Graph / Growth Frame
        frame_w, frame_h = 920, 680
        frame_x = (self.base_width - frame_w) // 2
        frame_y = 390
        draw.rounded_rectangle(
            [frame_x, frame_y, frame_x + frame_w, frame_y + frame_h],
            radius=28,
            fill=(20, 27, 40, 240),
            outline=(0, 230, 118, 160),
            width=2,
        )

        # Compounding Curve & Steps
        step_pts = [
            (frame_x + 80, frame_y + 540),
            (frame_x + 240, frame_y + 500),
            (frame_x + 420, frame_y + 420),
            (frame_x + 600, frame_y + 280),
            (frame_x + 820, frame_y + 100),
        ]
        # Draw curve path
        for i in range(len(step_pts) - 1):
            draw.line([step_pts[i], step_pts[i + 1]], fill=(0, 230, 118), width=6)
            # Glowing node
            pt = step_pts[i]
            draw.ellipse([pt[0] - 10, pt[1] - 10, pt[0] + 10, pt[1] + 10], fill=(255, 215, 0))

        # Final surging node
        last_pt = step_pts[-1]
        draw.ellipse([last_pt[0] - 16, last_pt[1] - 16, last_pt[0] + 16, last_pt[1] + 16], fill=(0, 230, 118))
        draw.text((last_pt[0] - 140, last_pt[1] - 50), "EXPONENTIAL", font=self._get_font(26, bold=True), fill=(0, 230, 118))

        # Year labels on timeline
        lbls = ["YEAR 1", "YEAR 5", "YEAR 10", "YEAR 20", "YEAR 30+"]
        for pt, lbl in zip(step_pts, lbls):
            draw.text((pt[0] - 40, pt[1] + 25), lbl, font=self._get_font(22, bold=False), fill=(148, 163, 184))

        # 4. Highlighted Stat Card
        stat_w, stat_h = 920, 240
        stat_x = (self.base_width - stat_w) // 2
        stat_y = 1130
        draw.rounded_rectangle(
            [stat_x, stat_y, stat_x + stat_w, stat_y + stat_h],
            radius=24,
            fill=(17, 24, 39, 230),
            outline=(255, 215, 0, 180),
            width=2,
        )
        draw.text((stat_x + 40, stat_y + 30), "WARREN BUFFETT CASE STUDY:", font=self._get_font(24, bold=True), fill=(255, 215, 0))
        t1 = "Over 99% of Warren Buffett's wealth was generated"
        t2 = "AFTER his 50th birthday. His real secret wasn't genius;"
        t3 = "his secret was staying in the game for 75 YEARS."
        draw.text((stat_x + 40, stat_y + 75), t1, font=self._get_font(28, bold=False), fill=(255, 255, 255))
        draw.text((stat_x + 40, stat_y + 115), t2, font=self._get_font(28, bold=False), fill=(255, 255, 255))
        draw.text((stat_x + 40, stat_y + 165), t3, font=self._get_font(30, bold=True), fill=(0, 230, 118))

        return img

    def _render_scene_4_rule(
        self, narration: str, book: str, hero_image_path: Optional[Path]
    ) -> Image.Image:
        """Scene 4: The Actionable Protocol / Document & Highlighter Callout."""
        w, h = self.base_width, self.base_height
        img = self._draw_base_stage(glow_color=(255, 215, 0), glow_cy=850)
        draw = ImageDraw.Draw(img)

        # 1. Pill
        self._draw_pill_badge(draw, f"{book}  ·  THE PROTOCOL", y=150, accent_color=(255, 215, 0))

        # 2. Headline
        font_hl = self._get_font(60, bold=True)
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), "THE 3 GOLDEN RULES", font=font_hl)[2]) // 2, 270),
            "THE 3 GOLDEN RULES",
            font=font_hl,
            fill=(255, 255, 255),
        )

        # 3. Document / Term Sheet Callout
        doc_w, doc_h = 920, 650
        doc_x = (self.base_width - doc_w) // 2
        doc_y = 390
        draw.rounded_rectangle(
            [doc_x, doc_y, doc_x + doc_w, doc_y + doc_h],
            radius=24,
            fill=(20, 26, 38, 245),
            outline=(255, 215, 0, 160),
            width=2,
        )

        rules = [
            ("RULE #1", "Never interrupt compounding unnecessarily.", "Patience beats trading IQ every single time."),
            ("RULE #2", "Define 'ENOUGH' before the goalposts move.", "Lifestyle inflation is the silent killer of wealth."),
            ("RULE #3", "Savings rate matters more than returns.", "You can control your spending; you cannot control the market."),
        ]
        ry = doc_y + 40
        for num, title, detail in rules:
            draw.text((doc_x + 40, ry), num, font=self._get_font(22, bold=True), fill=(255, 215, 0))
            draw.text((doc_x + 40, ry + 32), title, font=self._get_font(30, bold=True), fill=(255, 255, 255))
            draw.text((doc_x + 40, ry + 76), detail, font=self._get_font(24, bold=False), fill=(148, 163, 184))
            draw.line([(doc_x + 35, ry + 125), (doc_x + doc_w - 35, ry + 125)], fill=(40, 48, 66), width=1)
            ry += 160

        # Translucent highlighter bar over Rule 3
        hl_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        hl_draw = ImageDraw.Draw(hl_layer)
        hl_draw.rectangle([doc_x + 36, ry - 132, doc_x + 850, ry - 88], fill=(255, 215, 0, 65))
        img = Image.alpha_composite(img, hl_layer)
        draw = ImageDraw.Draw(img)

        # 4. Bottom Metric Pill
        callout_w, callout_h = 920, 150
        callout_x = (self.base_width - callout_w) // 2
        callout_y = 1100
        draw.rounded_rectangle(
            [callout_x, callout_y, callout_x + callout_w, callout_y + callout_h],
            radius=20,
            fill=(17, 24, 39, 230),
            outline=(0, 230, 118, 180),
            width=2,
        )
        draw.text((callout_x + 40, callout_y + 30), "ACTION STEP:", font=self._get_font(22, bold=True), fill=(0, 230, 118))
        draw.text(
            (callout_x + 40, callout_y + 70),
            "Automate 20% of your paycheck into index funds today.",
            font=self._get_font(28, bold=True),
            fill=(255, 255, 255),
        )

        return img

    def _render_scene_5_payoff(
        self, narration: str, book: str, hero_image_path: Optional[Path]
    ) -> Image.Image:
        """Scene 5: Triumphant Payoff / Freedom Equation."""
        img = self._draw_base_stage(glow_color=(0, 230, 118), glow_cy=800)
        draw = ImageDraw.Draw(img)

        # 1. Pill
        self._draw_pill_badge(draw, f"{book}  ·  THE ULTIMATE DIVIDEND", y=150, accent_color=(0, 230, 118))

        # 2. Main Headline
        font_hl = self._get_font(56, bold=True)
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), "THE HIGHEST DIVIDEND", font=font_hl)[2]) // 2, 270),
            "THE HIGHEST DIVIDEND",
            font=font_hl,
            fill=(255, 255, 255),
        )

        # 3. Central Freedom Equation Card
        eq_w, eq_h = 920, 600
        eq_x = (self.base_width - eq_w) // 2
        eq_y = 390
        draw.rounded_rectangle(
            [eq_x, eq_y, eq_x + eq_w, eq_y + eq_h],
            radius=32,
            fill=(20, 27, 40, 240),
            outline=(0, 230, 118, 200),
            width=3,
        )

        draw.text(
            ((self.base_width - draw.textbbox((0, 0), "TRUE WEALTH EQUATION", font=self._get_font(26, bold=True))[2]) // 2, eq_y + 40),
            "TRUE WEALTH EQUATION",
            font=self._get_font(26, bold=True),
            fill=(255, 215, 0),
        )

        # Big Gold Time / Freedom Equation
        lines = [
            "MONEY BUYS TIME",
            "+",
            "TIME BUYS FREEDOM",
            "=",
            "PEACE OF MIND",
        ]
        ly = eq_y + 110
        colors = [
            (255, 255, 255),
            (148, 163, 184),
            (0, 230, 118),
            (148, 163, 184),
            (255, 215, 0),
        ]
        fonts = [
            self._get_font(42, bold=True),
            self._get_font(32, bold=True),
            self._get_font(44, bold=True),
            self._get_font(32, bold=True),
            self._get_font(48, bold=True),
        ]
        for line, color, font in zip(lines, colors, fonts):
            lw = draw.textbbox((0, 0), line, font=font)[2]
            draw.text(((self.base_width - lw) // 2, ly), line, font=font, fill=color)
            ly += 80

        # 4. Final CTA Box
        cta_w, cta_h = 920, 180
        cta_x = (self.base_width - cta_w) // 2
        cta_y = 1050
        draw.rounded_rectangle(
            [cta_x, cta_y, cta_x + cta_w, cta_y + cta_h],
            radius=24,
            fill=(17, 24, 39, 230),
            outline=(255, 215, 0, 180),
            width=2,
        )
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), "MORGAN HOUSEL'S FINAL LESSON", font=self._get_font(22, bold=True))[2]) // 2, cta_y + 30),
            "MORGAN HOUSEL'S FINAL LESSON",
            font=self._get_font(22, bold=True),
            fill=(255, 215, 0),
        )
        msg = '"The ability to do what you want, when you want, with who you want, for as long as you want, is priceless."'
        lines_msg = [
            '"The ability to do what you want, when you want,',
            'with who you want, for as long as you want, is priceless."',
        ]
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), lines_msg[0], font=self._get_font(26, bold=False))[2]) // 2, cta_y + 75),
            lines_msg[0],
            font=self._get_font(26, bold=False),
            fill=(255, 255, 255),
        )
        draw.text(
            ((self.base_width - draw.textbbox((0, 0), lines_msg[1], font=self._get_font(26, bold=False))[2]) // 2, cta_y + 115),
            lines_msg[1],
            font=self._get_font(26, bold=False),
            fill=(0, 230, 118),
        )

        return img
