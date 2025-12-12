"""Application configuration using Pydantic Settings.

Loads configuration from environment variables with validation.
ISO/IEC 25010: Maintainability, Security
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings are validated using Pydantic with strict mode.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # Application
    # ==========================================================================
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_DEBUG: bool = True
    APP_LOG_LEVEL: Literal["debug", "info", "warning", "error", "critical"] = "info"
    APP_NAME: str = "Focus Mate"
    APP_VERSION: str = "1.0.0"

    # ==========================================================================
    # Server
    # ==========================================================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    WORKERS: int = 4

    # ==========================================================================
    # Database
    # ==========================================================================
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/focus_mate",
        description="Database connection URL",
    )
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("sqlite+aiosqlite://", "postgresql+asyncpg://")):
            raise ValueError(
                "DATABASE_URL must start with sqlite+aiosqlite:// or postgresql+asyncpg://"
            )
        return v

    # ==========================================================================
    # Redis
    # ==========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_DECODE_RESPONSES: bool = True

    # ==========================================================================
    # Security
    # ==========================================================================
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        min_length=32,
        description="Secret key for JWT encoding",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Admin Configuration
    ADMIN_EMAIL: str = Field(
        default="admin@focusmate.dev",
        description="Admin email for development environment",
    )

    BCRYPT_ROUNDS: int = Field(default=12, ge=10, le=14)

    # ==========================================================================
    # CORS
    # ==========================================================================
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:8080"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = Field(default="*")
    CORS_ALLOW_HEADERS: str = Field(default="*")

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                import json
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("CORS_ALLOW_METHODS")
    @classmethod
    def parse_cors_methods(cls, v: str) -> list[str]:
        """Parse CORS methods."""
        if isinstance(v, list):
            return v
        if v == "*":
            return ["*"]
        if isinstance(v, str):
            return [method.strip() for method in v.split(",") if method.strip()]
        return ["*"]

    @field_validator("CORS_ALLOW_HEADERS")
    @classmethod
    def parse_cors_headers(cls, v: str) -> list[str]:
        """Parse CORS headers."""
        if isinstance(v, list):
            return v
        if v == "*":
            return ["*"]
        if isinstance(v, str):
            return [header.strip() for header in v.split(",") if header.strip()]
        return ["*"]

    # ==========================================================================
    # Rate Limiting
    # ==========================================================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # ==========================================================================
    # WebSocket
    # ==========================================================================
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS_PER_ROOM: int = 50

    # ==========================================================================
    # Email (SMTP)
    # ==========================================================================
    SMTP_ENABLED: bool = False
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@focusmate.com"
    SMTP_FROM_NAME: str = "Focus Mate"
    SMTP_USE_TLS: bool = True

    # ==========================================================================
    # File Storage
    # ==========================================================================
    STORAGE_TYPE: Literal["local", "s3"] = "local"
    STORAGE_LOCAL_PATH: str = "./uploads"
    STORAGE_MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AWS S3 (optional)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_S3_REGION: str = "us-east-1"

    # ==========================================================================
    # Push Notifications
    # ==========================================================================
    FCM_ENABLED: bool = False
    FCM_SERVER_KEY: str = ""

    # ==========================================================================
    # Monitoring
    # ==========================================================================
    PROMETHEUS_ENABLED: bool = False
    PROMETHEUS_PORT: int = 9090

    SENTRY_ENABLED: bool = False
    SENTRY_DSN: str = ""

    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""

    # ==========================================================================
    # Feature Flags
    # ==========================================================================
    FEATURE_COMMUNITY_ENABLED: bool = False
    FEATURE_MESSAGING_ENABLED: bool = False
    FEATURE_STATS_ENABLED: bool = False
    FEATURE_ACHIEVEMENTS_ENABLED: bool = False
    FEATURE_NOTIFICATIONS_ENABLED: bool = False

    # ==========================================================================
    # Development
    # ==========================================================================
    DEV_SEED_DATA: bool = False
    DEV_RESET_DB: bool = False

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings

    Example:
        ```python
        from app.core.config import get_settings

        settings = get_settings()
        print(settings.APP_NAME)
        ```
    """
    return Settings()


# Global settings instance
settings = get_settings()
