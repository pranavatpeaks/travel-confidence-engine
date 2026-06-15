from __future__ import annotations

import asyncio
import logging
import sys

from telegram import __version__ as TG_VERSION
from telegram.ext import Application

from bot.handlers import register_handlers
from config import get_settings
from db.models import create_tables


def configure_logging(log_level: int) -> None:

    logging.basicConfig(
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=log_level,
        stream=sys.stdout,
    )

    if log_level > logging.DEBUG:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)


def build_application(
    token: str,
) -> Application:

    return (
        Application.builder()
        .token(token)
        .build()
    )


def main() -> None:

    try:
        asyncio.get_event_loop()

    except RuntimeError:

        loop = asyncio.new_event_loop()

        asyncio.set_event_loop(
            loop
        )

    settings = get_settings()

    configure_logging(
        settings.log_level_int
    )

    logger = logging.getLogger(__name__)

    logger.info(
        "Starting Travel Booking Confidence Engine "
        "(python-telegram-bot %s, log_level=%s)",
        TG_VERSION,
        settings.log_level,
    )

    create_tables()

    logger.info(
        "Database ready."
    )

    app = build_application(
        settings.bot_token
    )

    register_handlers(app)

    logger.info(
        "Handlers registered — entering polling loop."
    )

    app.run_polling(
        drop_pending_updates=True,
        close_loop=True,
    )


if __name__ == "__main__":
    main()