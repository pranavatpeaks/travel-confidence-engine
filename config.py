from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Telegram ──────────────────────────────────────────────────────────────
    bot_token: str = Field(
        ...,
        description="Telegram Bot API token (from BotFather).",
    )

    # ── Database ──────────────────────────────────────────────────────────────
    db_path: Path = Field(
        default=Path("data/travel.db"),
        description="Path to the SQLite database file.",
    )

    # ── Scraping ──────────────────────────────────────────────────────────────
    scrape_interval_hours: int = Field(
        default=4,
        ge=1,
        le=24,
        description="How often (in hours) to scrape fares for active trackers.",
    )
    scrape_timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Per-page Selenium timeout in seconds.",
    )
    scrape_max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts per scrape before marking a failure.",
    )
    headless: bool = Field(
        default=True,
        description="Run Chrome in headless mode (set False for local debugging).",
    )

    # ── Notifications ─────────────────────────────────────────────────────────
    daily_summary_hour: int = Field(
        default=20,
        ge=0,
        le=23,
        description="Hour (24-h, IST) at which daily fare summaries are sent.",
    )
    fare_change_threshold_pct: float = Field(
        default=5.0,
        ge=0.0,
        le=100.0,
        description="Minimum % fare change that triggers an immediate notification.",
    )

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = Field(
        default="INFO",
        description="Python logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
    )

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("bot_token")
    @classmethod
    def bot_token_must_be_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("BOT_TOKEN must not be empty.")
        # Telegram tokens are formatted as <numeric_id>:<alphanumeric_secret>
        if ":" not in v:
            raise ValueError(
                "BOT_TOKEN looks malformed — expected '<id>:<secret>' from BotFather."
            )
        return v

    @field_validator("log_level")
    @classmethod
    def log_level_must_be_valid(cls, v: str) -> str:
        v = v.upper()
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v not in valid:
            raise ValueError(f"LOG_LEVEL must be one of {valid}, got '{v}'.")
        return v

    @model_validator(mode="after")
    def ensure_db_directory_exists(self) -> Settings:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return self

    # ── Convenience helpers ───────────────────────────────────────────────────

    @property
    def log_level_int(self) -> int:
        """Return the numeric logging constant for the configured level."""
        return getattr(logging, self.log_level)

    @property
    def db_url(self) -> str:
        """SQLite connection URL (compatible with SQLAlchemy / SQLModel)."""
        return f"sqlite:///{self.db_path.resolve()}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton Settings instance.

    Import and call this everywhere instead of instantiating Settings directly:

        from config import get_settings
        settings = get_settings()
    """
    return Settings()