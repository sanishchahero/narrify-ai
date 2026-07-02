from pydantic import BaseModel


class SceneResponse(BaseModel):
    id: int
    title: str
    narration: str
    visual_prompt: str
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
    style: str
    scenes: list[SceneResponse]