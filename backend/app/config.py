"""ProofChain configuration — all settings from environment variables."""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AWS
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")

    # Bedrock
    bedrock_model_id: str = os.getenv(
        "BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-20250514-v1:0"
    )
    bedrock_embedding_model_id: str = os.getenv(
        "BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0"
    )

    # Storage
    s3_bucket: str = os.getenv("S3_BUCKET", "proofchain-documents")
    dynamodb_table: str = os.getenv("DYNAMODB_TABLE", "proofchain-state")

    # App
    environment: str = os.getenv("PROOFCHAIN_ENV", "development")
    max_upload_size_mb: int = 10
    allowed_file_types: list[str] = [".pdf", ".docx", ".txt", ".md"]

    # Agent
    agent_timeout_seconds: int = 300
    max_retries: int = 2

    # Demo
    demo_mode: bool = os.getenv("DEMO_MODE", "false").lower() == "true"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
