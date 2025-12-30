from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Union
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "AI-Ops Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security - SECRET_KEY must be set via environment variable
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    SECRET_KEY: str = Field(
        default=...,  # Required - no default for security
        description="JWT signing key - must be set via SECRET_KEY environment variable"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/aiops"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # CORS
    CORS_ORIGINS: Union[List[str], str] = Field(default=["http://localhost:3000", "http://localhost:5173"])
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Email (for password reset)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@aiops.local"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")

    # AI/ML Settings (Anthropic Claude)
    # Supports both API keys (sk-ant-api...) and OAuth tokens (sk-ant-oat...)
    # IMPORTANT: Set via ANTHROPIC_API_KEY environment variable - never hardcode!
    ANTHROPIC_API_KEY: str = Field(
        default="",  # Empty default - AI features disabled if not set
        description="Anthropic API key - must be set via ANTHROPIC_API_KEY environment variable"
    )
    ANTHROPIC_MODEL: str = Field(default="claude-sonnet-4-20250514")
    AI_CLASSIFICATION_ENABLED: bool = True
    AI_SUGGESTION_ENABLED: bool = True
    AI_CORRELATION_ENABLED: bool = True
    AI_CONFIDENCE_THRESHOLD: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
