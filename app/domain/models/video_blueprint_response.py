from pydantic import BaseModel, Field


class VisualContextResponse(BaseModel):
    art_style: str
    color_palette: str
    aspect_ratio: str
    illustration_style: str
    narrator_style: str
    recurring_characters: list[str]


class SceneResponse(BaseModel):
    id: int
    title: str
    narration: str
    subject: str
    action: str
    background: str
    foreground: str
    composition: str
    perspective: str
    lighting: str
    camera_motion: str
    transition: str
    emotion: str
    music_mood: str
    subtitle_style: str
    sound_effects: list[str]


class VideoBlueprintResponse(BaseModel):
    title: str
    hook: str
    ending: str
    visual_context: VisualContextResponse
    scenes: list[SceneResponse] = Field(min_length=5, max_length=7)


VideoBlueprintResponse.model_rebuild()