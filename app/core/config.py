from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Narrify AI"
    environment: str = "development"

    # LLM Settings
    llm_provider: str = "openrouter"  # "openrouter" or "ollama"
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Default OpenRouter model: Llama 3.3 70B (open source, high quality, 128k context)
    llm_model: str = "meta-llama/llama-3.3-70b-instruct"
    llm_temperature: float = 0.7

    # Image Generation Settings
    image_provider: str = "cloud"  # "cloud" (zero-local FLUX cloud) or "comfyui"
    image_model: str = "flux"

    # Ollama Fallback Settings
    ollama_host: str = "http://localhost:11434"

    output_directory: str = "output"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
