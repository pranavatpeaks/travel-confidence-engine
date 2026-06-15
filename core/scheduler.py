from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from core.orchestrator import collect_fares_once

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    """
    Start fare collection scheduler.

    Runs every 4 hours.
    """

    scheduler.add_job(
        collect_fares_once,
        trigger="interval",
        hours=1,
        id="fare_collection",
        replace_existing=True,
    )

    scheduler.start()

    logger.info(
        "Scheduler started (every 1 minutes)."
    )


def stop_scheduler() -> None:
    """
    Stop scheduler gracefully.
    """

    if scheduler.running:
        scheduler.shutdown()

        logger.info(
            "Scheduler stopped."
        )
