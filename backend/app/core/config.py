from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Application
    APP_ENV: str = "development"
    APP_NAME: str = "AstroMind AI"
    APP_BASE_URL: str = "http://localhost:3000"
    API_BASE_URL: str = "http://localhost:8000"
    LOG_LEVEL: str = "INFO"

    # Security & CORS
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AUTH_PER_MINUTE: int = 15
    RATE_LIMIT_CALCULATION_PER_MINUTE: int = 60
    RATE_LIMIT_AI_PER_MINUTE: int = 30
    RATE_LIMIT_REPORTS_PER_MINUTE: int = 10
    RATE_LIMIT_DEFAULT_PER_MINUTE: int = 120
    MAX_REQUEST_BODY_BYTES: int = 1048576  # 1 MB limit
    MAX_CHAT_INPUT_CHARS: int = 8000
    MAX_TOOL_CALLS_PER_TURN: int = 5

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgrespassword_dev@localhost:5432/astromind"
    SUPABASE_URL: str = "http://localhost:54321"
    SUPABASE_ANON_KEY: str = "dev-anon-key-placeholder"
    SUPABASE_SERVICE_ROLE_KEY: str = "dev-service-role-key-placeholder"

    # AI Configuration (Server-Side)
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = "dummy-key-for-dev"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MAX_OUTPUT_TOKENS: int = 1500
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_DAILY_BUDGET_USD: float = 10.0

    # Embeddings
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # Redis & Workers
    REDIS_URL: str = "redis://localhost:6379/0"
    WORKER_QUEUE_NAME: str = "astromind-jobs"

    # Storage
    REPORT_STORAGE_PROVIDER: str = "local"
    REPORT_BUCKET: str = "astromind-private-reports"
    SIGNED_URL_TTL_SECONDS: int = 300

    # Vedic Astrology Engine
    ASTROLOGY_ENGINE: str = "pyswisseph"
    ASTROLOGY_ENGINE_VERSION: str = "2.10.3"
    ASTROLOGY_CONFIG_VERSION: str = "vedic-v1"
    ASTROLOGY_AYANAMSA: str = "lahiri"
    ASTROLOGY_NODE_MODE: str = "mean"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() in ("production", "prod")

    @field_validator("CORS_ALLOWED_ORIGINS")
    @classmethod
    def validate_cors(cls, v: str) -> str:
        origins = [o.strip() for o in v.split(",") if o.strip()]
        if "*" in origins:
            # Explicit security rule: never allow wildcard CORS with credentials
            raise ValueError("Wildcard '*' CORS origin is strictly prohibited for security.")
        return v


settings = Settings()
