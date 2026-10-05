from pydantic import BaseModel, Field


class SceneResponse(BaseModel):
    id: int
    duration: int = 6
    narration: str
    visual_goal: str
    emotion: str = "curious"


class ScriptResponse(BaseModel):
    title: str
    hook: str
    summary: str
    scenes: list[SceneResponse] = Field(..., min_length=4)
