from pydantic import BaseModel


class SceneResponse(BaseModel):
    id: int
    duration: int
    narration: str
    visual_goal: str
    emotion: str


class ScriptResponse(BaseModel):
    title: str
    hook: str
    summary: str
    scenes: list[SceneResponse]
