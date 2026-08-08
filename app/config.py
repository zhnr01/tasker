from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application configuration, read from the environment (or a .env file).

    Every field is typed and validated. If a required value is missing or a value
    can't be coerced to its type, construction raises at startup — we never limp
    along with half-configured state. (15-config.md: fail-closed.)
    """

    # env_prefix keeps our vars namespaced: TASKER_DATABASE_URL, TASKER_SECRET_KEY,
    # etc. — so they never collide with unrelated vars on the host.
    model_config = SettingsConfigDict(
        env_prefix="TASKER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Runtime -------------------------------------------------------------
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    DEBUG: bool = False
    PROJECT_NAME: str = "tasker"

    # --- Database ------------------------------------------------------------
    # A full DSN, e.g. postgresql+psycopg://tasker:tasker@localhost:5432/tasker
    # Allow either a PostgresDsn or a plain str so static type checkers
    # won't complain when a string literal is used as the default.
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+psycopg://tasker:tasker@localhost:5432/tasker"
    )
    # Connection-pool tunables (used in Part 03).
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # --- Redis (queue + cache, later parts) ----------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Security (Part 17) --------------------------------------------------
    # No safe default for a secret: we validate it's set in production below.
    SECRET_KEY: str = "dev-only-insecure-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    JWT_ALGORITHM: str = "HS256"

    # --- API behaviour -------------------------------------------------------
    API_V1_PREFIX: str = "/v1"
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    STATS_CACHE_TTL_SECONDS: int = 60

    # CORS allowlist (Part 24). Comma-separated in env, parsed to a list.
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # --- Derived helpers -----------------------------------------------------
    @computed_field  # exposed like a normal attribute: settings.is_production
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def model_post_init(self, __context) -> None:
        """Cross-field validation that runs after all fields are set.

        Enforces production-only invariants. This is the 'fail-closed' guard:
        the app refuses to boot in production with an insecure secret.
        """
        if self.is_production and self.SECRET_KEY == "dev-only-insecure-change-me":
            raise ValueError(
                "TASKER_SECRET_KEY must be set to a strong value in production."
            )


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide Settings, built exactly once.

    @lru_cache makes this a lazy singleton: the first call constructs and
    validates Settings; every later call returns the same instance. Import this
    function (never a module-level Settings) so tests can override the env before
    the first call and clear the cache between tests.
    """
    return Settings()
