from dataclasses import dataclass


@dataclass(frozen=True)
class RenderConfig:
    width: int = 512
    height: int = 896

    steps: int = 20
    cfg: float = 7.0

    sampler: str = "dpmpp_2m"
    scheduler: str = "karras"

    seed: int = 42


DEV_RENDER = RenderConfig()