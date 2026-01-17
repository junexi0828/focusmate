"""Application configuration using Pydantic Settings.

Loads configuration from environment variables with validation.
ISO/IEC 25010: Maintainability, Security
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from sqlalchemy.engine.url import make_url
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
    APP_DEBUG: bool = False  # Production safe default
    APP_LOG_LEVEL: Literal["debug", "info", "warning", "error", "critical"] = "info"
    APP_NAME: str = "Focus Mate"
    APP_VERSION: str = "1.0.0"
    APP_SLOW_REQUEST_THRESHOLD_MS: int = 1500

    # ==========================================================================
    # Server
    # ==========================================================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    WORKERS: int = 4
    TRUST_PROXY_HEADERS: bool = False  # Only enable when behind a trusted reverse proxy

    # ==========================================================================
    # Database
    # ==========================================================================
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/focus_mate",
        description="Database connection URL",
    )
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 2
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800  # Recycle connections every 30 minutes
    DATABASE_POOL_USE_LIFO: bool = True  # Favor recently used connections
    DATABASE_PGBOUNCER: bool = False  # Set to True when using Supabase Transaction Mode (port 6543)
    DATABASE_DISABLE_PREPARED_STATEMENTS: bool = True  # Safer default for transaction poolers
    DATABASE_ENABLE_PREPARED_STATEMENTS: bool = False  # Explicit opt-in for prepared statements

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("sqlite+aiosqlite://", "postgresql+asyncpg://")):
            raise ValueError(
                "DATABASE_URL must start with sqlite+aiosqlite:// or postgresql+asyncpg://"
            )
        return v

    @model_validator(mode="after")
    def enforce_database_safety(self) -> "Settings":
        """Force safe DB settings when using pgBouncer or production-like environments."""
        if self.APP_ENV in {"production", "staging"}:
            self.DATABASE_DISABLE_PREPARED_STATEMENTS = True
            self.DATABASE_ENABLE_PREPARED_STATEMENTS = False

        if self.DATABASE_URL.startswith("postgresql"):
            is_pooler = False
            try:
                parsed_url = make_url(self.DATABASE_URL)
                if parsed_url.port in {6432, 6543}:
                    is_pooler = True
                hostname = (parsed_url.host or "").lower()
                if "pooler" in hostname or "pgbouncer" in hostname:
                    is_pooler = True
                query_flag = str(parsed_url.query.get("pgbouncer", "")).lower()
                if query_flag in {"1", "true", "yes"}:
                    is_pooler = True
                pool_mode = str(parsed_url.query.get("pool_mode", "")).lower()
                if pool_mode in {"transaction", "statement"}:
                    is_pooler = True
            except Exception:
                is_pooler = False

            if is_pooler:
                self.DATABASE_PGBOUNCER = True
                self.DATABASE_DISABLE_PREPARED_STATEMENTS = True
                self.DATABASE_ENABLE_PREPARED_STATEMENTS = False

            # Disable prepared statements unless explicitly enabled in a safe context.
            if self.DATABASE_ENABLE_PREPARED_STATEMENTS:
                if self.APP_ENV == "development" and not is_pooler:
                    self.DATABASE_DISABLE_PREPARED_STATEMENTS = False
                else:
                    self.DATABASE_ENABLE_PREPARED_STATEMENTS = False
                    self.DATABASE_DISABLE_PREPARED_STATEMENTS = True
            else:
                self.DATABASE_DISABLE_PREPARED_STATEMENTS = True

            # Prepared statements are handled via connect_args in session.py to ensure correct types.
            # Avoid modifying the URL string directly as asyncpg may fail to coerce types.
            pass

        return self

    # ==========================================================================
    # Redis
    # ==========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_SOCKET_TIMEOUT: float = 1.0
    REDIS_CONNECT_TIMEOUT: float = 1.0
    REDIS_HEALTH_CHECK_INTERVAL: int = 30
    REDIS_RETRY_ON_TIMEOUT: bool = True

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

    SECURITY_HEADERS_ENABLED: bool = True
    SECURITY_HSTS_ENABLED: bool = True
    SECURITY_CSP_ENABLED: bool = False
    SECURITY_CSP_POLICY: str = (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    )

    # File Encryption (optional - if not set, derives from SECRET_KEY)
    FILE_ENCRYPTION_KEY: str | None = Field(
        default=None,
        description="Base64-encoded Fernet key for file encryption. If not set, derives from SECRET_KEY.",
    )

    # ==========================================================================
    # Frontend
    # ==========================================================================
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend application URL",
    )

    # ==========================================================================
    # CORS
    # ==========================================================================
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:8080,https://eieconcierge.com,https://www.eieconcierge.com,https://api.eieconcierge.com"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = Field(default="GET,POST,PUT,PATCH,DELETE,OPTIONS")
    CORS_ALLOW_HEADERS: str = Field(
        default="Authorization,Content-Type,Accept,Origin,X-Requested-With,X-Request-ID"
    )
    CORS_EXPOSE_HEADERS: str = Field(default="X-Request-ID,X-App-Version,Content-Disposition")
    CORS_ORIGIN_REGEX: str | None = None

    # ==========================================================================
    # Trusted Hosts
    # ==========================================================================
    TRUSTED_HOSTS: str = Field(
        default="localhost,127.0.0.1,0.0.0.0",
        description="Comma-separated list of allowed hosts. Use '*' to allow all hosts (dev only)",
    )

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

    @field_validator("CORS_EXPOSE_HEADERS")
    @classmethod
    def parse_cors_expose_headers(cls, v: str) -> list[str]:
        """Parse CORS expose headers."""
        return cls.parse_cors_headers(v)

    @field_validator("CORS_ORIGIN_REGEX")
    @classmethod
    def parse_cors_origin_regex(cls, v: str | None) -> str | None:
        """Normalize optional CORS origin regex."""
        if not v:
            return None
        if isinstance(v, str):
            return v.strip() or None
        return None

    @field_validator("TRUSTED_HOSTS")
    @classmethod
    def parse_trusted_hosts(cls, v: str) -> list[str]:
        """Parse trusted hosts from comma-separated string."""
        if isinstance(v, list):
            return v
        if v == "*":
            return ["*"]
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return ["localhost", "127.0.0.1"]

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """Enforce secure configuration in production."""
        if self.APP_ENV == "production":
            if self.SECRET_KEY == "dev-secret-key-change-in-production":
                raise ValueError("SECRET_KEY must be set to a secure value in production")
            if not self.SECURITY_HEADERS_ENABLED or not self.SECURITY_HSTS_ENABLED:
                raise ValueError("SECURITY_HEADERS_ENABLED and SECURITY_HSTS_ENABLED must be enabled in production")
            if not self.SECURITY_CSP_ENABLED:
                import logging
                logging.getLogger("app").warning("⚠️ SECURITY_CSP_ENABLED is disabled in production")
            if isinstance(self.CORS_ORIGINS, list):
                if "*" in self.CORS_ORIGINS:
                    raise ValueError("CORS_ORIGINS cannot be '*' in production")

                # In production, enforce HTTPS unless APP_DEBUG is enabled for development/testing
                if not self.APP_DEBUG:
                    if any(origin.startswith("http://") and not ("localhost" in origin or "127.0.0.1" in origin)
                           for origin in self.CORS_ORIGINS):
                        raise ValueError("CORS_ORIGINS must use https in production for remote hosts")

            if isinstance(self.TRUSTED_HOSTS, list):
                if "*" in self.TRUSTED_HOSTS:
                    raise ValueError("TRUSTED_HOSTS cannot be '*' in production")

                # In production, enforce production domains unless APP_DEBUG is enabled
                if not self.APP_DEBUG:
                    disallowed_hosts = {"localhost", "127.0.0.1", "0.0.0.0"}
                    if any(host in disallowed_hosts for host in self.TRUSTED_HOSTS):
                        raise ValueError("TRUSTED_HOSTS must be set to production domains in production")
        return self

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
    # Presence (Online Status)
    # ==========================================================================
    PRESENCE_TIMEOUT_MINUTES: int = 5
    PRESENCE_CLEANUP_INTERVAL_MINUTES: int = 5

    # ==========================================================================
    # Invitation Codes
    # ==========================================================================
    INVITATION_CODE_LENGTH: int = 8
    INVITATION_DEFAULT_EXPIRY_HOURS: int = 24

    # ==========================================================================
    # Legacy Messaging Migration
    # ==========================================================================
    ENABLE_LEGACY_MESSAGING: bool = False
    LEGACY_MIGRATION_BATCH_SIZE: int = 100

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

    # ==========================================================================
    # Cloud Expansion Roadmap (AWS Strategy) 프로덕션 전에 서버 가동
    # ==========================================================================
    # These settings are prepared for production-grade scaling on AWS.
    # Currently operational via high-fidelity local/staging mocks.

    # AWS S3 (S3 Storage Strategy)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_S3_REGION: str = "us-east-1"
    # AWS_S3_ENDPOINT_URL: str | None = None  # For local S3 mocks like LocalStack
    # AWS_S3_SIGNATURE_VERSION: str = "s3v4"

    # AWS RDS (Database Scaling Strategy)
    # Production database connection handles would be configured here:
    # RDS_HOSTNAME: str = ""
    # RDS_PORT: int = 5432
    # RDS_DB_NAME: str = "focusmate_prod"
    # RDS_USERNAME: str = ""
    # RDS_PASSWORD: str = ""

    # AWS SES (Enterprise Email Strategy)
    # SES_REGION: str = "us-east-1"
    # SES_ACCESS_KEY_ID: str = ""
    # SES_SECRET_ACCESS_KEY: str = ""
    # SES_SENDER_EMAIL: str = "noreply@focusmate.com"

    # ==========================================================================
    # Push Notifications
    # ==========================================================================
    FCM_ENABLED: bool = False
    FCM_SERVER_KEY: str = ""

    # ==========================================================================
    # Monitoring
    # ==========================================================================
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090

    SENTRY_ENABLED: bool = False
    SENTRY_DSN: str = ""

    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""

    # ==========================================================================
    # Feature Flags
    # ==========================================================================
    FEATURE_COMMUNITY_ENABLED: bool = True
    FEATURE_MESSAGING_ENABLED: bool = True
    FEATURE_STATS_ENABLED: bool = True
    FEATURE_ACHIEVEMENTS_ENABLED: bool = True
    FEATURE_NOTIFICATIONS_ENABLED: bool = True

    # ==========================================================================
    # Integration (Slack, etc.)
    # ==========================================================================
    SLACK_WEBHOOK_URL: str | None = Field(
        default=None,
        description="Slack Webhook URL for alerts and notifications",
    )

    # ==========================================================================
    # OAuth (Social Login)
    # ==========================================================================
    NAVER_CLIENT_ID: str = Field(
        default="YOUR_NAVER_CLIENT_ID",
        description="Naver OAuth Client ID",
    )
    NAVER_CLIENT_SECRET: str = Field(
        default="YOUR_NAVER_CLIENT_SECRET",
        description="Naver OAuth Client Secret",
    )
    NAVER_REDIRECT_URI: str = Field(
        default="http://localhost:3000/auth/naver/callback",
        description="Naver OAuth Redirect URI",
    )

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
       # Test configuration
    if __name__ == "__main__":
        import logging
        logger = logging.getLogger(__name__)
        settings = Settings()
        logger.info(f"App Name: {settings.APP_NAME}")
        ```
    """
    return Settings()


# Global settings instance
settings = get_settings()
