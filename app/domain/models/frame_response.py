from pydantic import BaseModel, Field


class FrameResponse(BaseModel):
    primary_subject: str

    primary_action: str

    subject_description: str

    secondary_subjects: list[str] = Field(default_factory=list)

    important_objects: list[str] = Field(default_factory=list)

    foreground: list[str] = Field(default_factory=list)

    middle_ground: list[str] = Field(default_factory=list)

    background: list[str] = Field(default_factory=list)

    visual_metaphor: str | None = None
