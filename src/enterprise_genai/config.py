from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env."""

    aws_region: str = "us-east-1"
    aws_profile: str | None = "genai-course"
    bedrock_text_model_id: str | None = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    bedrock_embedding_model_id: str | None = "amazon.titan-embed-text-v2:0"
    bedrock_image_model_id: str | None = "stability.stable-image-core-v1:1"
    bedrock_image_region: str = "us-west-2"
    course_debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
