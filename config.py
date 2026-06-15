from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    def __init__(self) -> None:

        self.bot_token = os.getenv("BOT_TOKEN", "").strip()

        if not self.bot_token:
            raise ValueError(
                "BOT_TOKEN environment variable is required."
            )

        self.log_level = (
            os.getenv("LOG_LEVEL", "INFO")
            .upper()
            .strip()
        )

    @property
    def log_level_int(self) -> int:

        return getattr(
            logging,
            self.log_level,
            logging.INFO,
        )


def get_settings() -> Settings:
    return Settings()