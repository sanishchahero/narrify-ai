from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Narrify AI"

    environment: str = "development"

    ollama_host: str = "http://localhost:11434"

    llm_model: str = "qwen3:8b"

    output_directory: str = "app/generated"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
