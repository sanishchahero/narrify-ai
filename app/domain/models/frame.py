from dataclasses import dataclass


@dataclass(slots=True)
class Frame:
    primary_subject: str

    primary_action: str

    subject_description: str

    secondary_subjects: list[str]

    important_objects: list[str]

    foreground: list[str]

    middle_ground: list[str]

    background: list[str]

    visual_metaphor: str | None = None
