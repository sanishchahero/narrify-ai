from pydantic import BaseModel, Field

from app.domain.models.camera_response import CameraResponse
from app.domain.models.character_response import CharacterResponse
from app.domain.models.environment_response import EnvironmentResponse
from app.domain.models.frame_response import FrameResponse


class SceneResponse(BaseModel):
    id: int = Field(..., ge=1)

    title: str

    narration: str

    frame: FrameResponse

    camera: CameraResponse

    environment: EnvironmentResponse

    characters: list[CharacterResponse] = Field(default_factory=list)

    emotion: str

    music_mood: str

    subtitle_style: str

    sound_effects: list[str] = Field(default_factory=list)
