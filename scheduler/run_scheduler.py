from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from core.orchestrator import collect_fares_once


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def scheduled_collection() -> None:

    logger.info(
        "Starting scheduled collection cycle..."
    )

    collect_fares_once()

    logger.info(
        "Scheduled collection cycle completed."
    )


scheduler = BlockingScheduler()

scheduler.add_job(
    scheduled_collection,
    trigger="interval",
    hours=3,
)

logger.info(
    "Scheduler initialized."
)

logger.info(
    "Running startup collection cycle..."
)

collect_fares_once()

logger.info(
    "Startup collection cycle completed."
)

logger.info(
    "Scheduler starting (every 3 hours)."
)

scheduler.start()