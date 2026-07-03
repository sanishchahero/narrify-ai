from pydantic import BaseModel


class CameraResponse(BaseModel):
    shot: str

    angle: str

    lens: str

    focus: str

    composition: str