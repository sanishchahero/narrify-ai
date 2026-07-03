from dataclasses import dataclass, field


@dataclass(slots=True)
class VisualContext:
    """
    Global visual rules shared by every scene.
    """

    art_style: str
    color_palette: str
    aspect_ratio: str
    illustration_style: str
    narrator_style: str
    recurring_characters: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Scene:
    id: int

    title: str

    narration: str

    # ---------- Visual Content ----------
    subject: str
    action: str
    background: str
    foreground: str

    # ---------- Composition ----------
    composition: str
    perspective: str
    lighting: str

    # ---------- Rendering ----------
    camera_motion: str
    transition: str

    # ---------- Emotion ----------
    emotion: str
    music_mood: str
    subtitle_style: str

    sound_effects: list[str] = field(default_factory=list)

    duration: float = 0.0


@dataclass(slots=True)
class VideoBlueprint:
    title: str

    hook: str

    ending: str

    total_duration: float

    visual_context: VisualContext

    scenes: list[Scene]
