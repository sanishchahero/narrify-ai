from pydantic import BaseModel, Field

from app.domain.models.character_response import CharacterResponse
from app.domain.models.scene_response import SceneResponse
from app.domain.models.visual_context_response import VisualContextResponse


class StoryboardResponse(BaseModel):
    title: str

    hook: str

    ending: str

    visual_context: VisualContextResponse

    character_bible: list[CharacterResponse] = Field(default_factory=list)

    scenes: list[SceneResponse] = Field(
        min_length=6,
        max_length=6,
    )


StoryboardResponse.model_rebuild()
