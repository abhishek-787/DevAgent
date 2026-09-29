import os

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


ENV_FILE = os.getenv(
    "DEVAGENT_ENV_FILE",
    ".env",
)


class Settings(BaseSettings):
    app_name: str = "DevAgent"

    ollama_base_url: str = (
        "http://192.168.0.7:11434"
    )

    coding_model: str = (
        "gemma4:31b-cloud"
    )

    general_model: str = (
    "llama3.2:3b"
)

    vision_model: str = (
        "qwen3-vl:4b"
    )

    embedding_model: str = (
        "nomic-embed-text:latest"
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()