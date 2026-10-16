from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env."""

    aws_region: str = "us-east-1"
    aws_profile: str | None = None
    bedrock_text_model_id: str | None = None
    bedrock_embedding_model_id: str | None = None
    bedrock_image_model_id: str | None = None
    course_debug: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
