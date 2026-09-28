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
    app_name: str

    ollama_base_url: str

    coding_model: str
    general_model: str
    vision_model: str
    embedding_model: str

    database_url: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()