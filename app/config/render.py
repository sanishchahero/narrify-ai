from dataclasses import dataclass


@dataclass(frozen=True)
class RenderConfig:
    width: int = 576
    height: int = 1024

    steps: int = 8
    cfg: float = 5.0

    sampler: str = "dpmpp_2m"
    scheduler: str = "karras"

    seed: int = 42


DEV_RENDER = RenderConfig()