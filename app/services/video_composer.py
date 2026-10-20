from pathlib import Path
from typing import Any, List, Optional, Tuple

import imageio_ffmpeg
import numpy as np
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_audioclips,
    concatenate_videoclips,
)
import moviepy.video.fx as vfx
from PIL import Image, ImageDraw, ImageFont

from app.services.subtitle_renderer import SubtitleRenderer


class VideoComposer:
    """
    Assembles scene images, voiceover audio, dynamic Ken Burns motion,
    and stylized subtitles into a polished vertical video (9:16, 1080x1920).
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = (1080, 1920),
        fps: int = 30,
    ):
        self.target_width, self.target_height = target_size
        self.fps = fps
        self.subtitle_renderer = SubtitleRenderer()
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def _prepare_scene_image(
        self,
        image_path: Optional[Path],
        scene_title: str,
        scene_id: int,
    ) -> np.ndarray:
        """
        Loads and fits the scene image to 1080x1920, or creates an aesthetic
        placeholder card if the image has not been rendered yet.
        """
        if image_path and Path(image_path).exists():
            img = Image.open(image_path).convert("RGB")
            # Calculate aspect fill
            img_ratio = img.width / img.height
            target_ratio = self.target_width / self.target_height

            if img_ratio > target_ratio:
                # Image is wider: fit height and crop width
                new_h = self.target_height
                new_w = int(new_h * img_ratio)
            else:
                # Image is taller: fit width and crop height
                new_w = self.target_width
                new_h = int(new_w / img_ratio)

            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            # Center crop
            left = (new_w - self.target_width) // 2
            top = (new_h - self.target_height) // 2
            final_img = img_resized.crop(
                (left, top, left + self.target_width, top + self.target_height)
            )
            return np.array(final_img)

        # Fallback aesthetic title card
        card = Image.new("RGB", (self.target_width, self.target_height), (22, 24, 30))
        draw = ImageDraw.Draw(card)

        # Subtle gradient or border accents
        draw.rectangle(
            [40, 40, self.target_width - 40, self.target_height - 40],
            outline=(70, 75, 95),
            width=3,
        )

        font = self.subtitle_renderer.font
        draw.text(
            (self.target_width // 2, self.target_height // 2 - 120),
            f"SCENE {scene_id}",
            font=font,
            fill=(220, 180, 80),
            anchor="mm",
        )
        draw.text(
            (self.target_width // 2, self.target_height // 2 - 20),
            scene_title,
            font=font,
            fill=(250, 250, 250),
            anchor="mm",
        )
        return np.array(card)

    def create_scene_clip(
        self,
        image_np: np.ndarray,
        narration: str,
        audio_path: Optional[Path],
        duration: float,
        zoom_in: bool = True,
    ) -> CompositeVideoClip:
        """
        Creates a single animated scene clip with Ken Burns motion,
        attached voiceover audio, and overlay subtitles.
        """
        # Base background image clip
        base_clip = ImageClip(image_np).with_duration(duration)

        # Ken Burns zoom effect
        if zoom_in:
            base_clip = base_clip.with_effects([
                vfx.Resize(lambda t: 1.0 + 0.04 * (t / max(duration, 0.1))),
                vfx.Crop(width=self.target_width, height=self.target_height),
            ])
        else:
            base_clip = base_clip.with_effects([
                vfx.Resize(lambda t: 1.04 - 0.04 * (t / max(duration, 0.1))),
                vfx.Crop(width=self.target_width, height=self.target_height),
            ])

        # Subtitle overlay
        layers = [base_clip]
        if narration and narration.strip():
            sub_img = self.subtitle_renderer.render_overlay(
                narration.strip(),
                video_size=(self.target_width, self.target_height),
            )
            sub_clip = ImageClip(np.array(sub_img), is_mask=False).with_duration(duration)
            layers.append(sub_clip)

        scene_composite = CompositeVideoClip(layers, size=(self.target_width, self.target_height))

        # Attach audio if available
        if audio_path and Path(audio_path).exists():
            audio_clip = AudioFileClip(str(audio_path))
            scene_composite = scene_composite.with_audio(audio_clip)

        return scene_composite

    def compose_video(
        self,
        scenes_data: List[dict[str, Any]],
        output_path: Path,
        bg_music_path: Optional[Path] = None,
        bg_music_volume: float = 0.08,
    ) -> Path:
        """
        Compiles multiple scene clips into a single .mp4 file.
        Each item in scenes_data must have:
            - title: str
            - narration: str
            - image_path: Optional[Path]
            - audio_path: Optional[Path]
            - duration: float
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        scene_clips = []
        for idx, s in enumerate(scenes_data):
            img_np = self._prepare_scene_image(
                image_path=s.get("image_path"),
                scene_title=s.get("title", f"Scene {idx+1}"),
                scene_id=s.get("id", idx + 1),
            )
            clip = self.create_scene_clip(
                image_np=img_np,
                narration=s.get("narration", ""),
                audio_path=s.get("audio_path"),
                duration=max(s.get("duration", 3.0), 1.0),
                zoom_in=(idx % 2 == 0),
            )
            scene_clips.append(clip)

        # Concatenate scenes
        final_video = concatenate_videoclips(scene_clips, method="compose")

        # Mix ambient background soundtrack if available
        music_file = bg_music_path if bg_music_path and Path(bg_music_path).exists() else Path("assets/audio/ambient_pad.mp3")
        music_clip = None
        if music_file and music_file.exists():
            try:
                raw_music = AudioFileClip(str(music_file))
                if raw_music.duration < final_video.duration:
                    n_loops = int(final_video.duration / raw_music.duration) + 1
                    raw_music = concatenate_audioclips([raw_music] * n_loops)
                music_clip = raw_music.subclipped(0, final_video.duration).with_volume_scaled(bg_music_volume)
                if final_video.audio:
                    mixed_audio = CompositeAudioClip([final_video.audio, music_clip])
                    final_video = final_video.with_audio(mixed_audio)
                else:
                    final_video = final_video.with_audio(music_clip)
                print(f"🎵 Mixed ambient background music (ducked at {int(bg_music_volume*100)}% volume)")
            except Exception as e:
                print(f"⚠️ Could not mix background music: {e}")

        print(f"\n🎬 Rendering final video ({final_video.duration:.1f}s) to: {output_path}...")
        final_video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            ffmpeg_params=["-pix_fmt", "yuv420p"],
            logger="bar",
        )

        # Close clips to free memory
        for c in scene_clips:
            c.close()
        if music_clip:
            music_clip.close()
        final_video.close()

        print(f"✅ Video successfully created at: {output_path}\n")
        return output_path
