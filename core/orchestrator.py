from __future__ import annotations

import logging

from core.tracker import get_all_active_trackers
from db.fare_repository import insert_many_observations
from scrapers.redbus import RedBusScraper

logger = logging.getLogger(__name__)


def collect_fares_once() -> None:

    trackers = get_all_active_trackers()

    if not trackers:
        logger.info("No active trackers found.")
        return

    logger.info(
        "Starting collection cycle for %d trackers",
        len(trackers),
    )

    with RedBusScraper(
        timeout=60,
        max_retries=1,
        limit=10,
    ) as scraper:

        for tracker in trackers:

            try:

                observations = scraper.search(
                    source_city_id=tracker["source_id"],
                    destination_city_id=tracker["destination_id"],
                    journey_date=tracker["journey_date"],
                )

                inserted = insert_many_observations(
                    tracker_id=tracker["id"],
                    observations=observations,
                )

                logger.info(
                    (
                        "Tracker %s "
                        "(%s → %s) "
                        "inserted %d observations"
                    ),
                    tracker["id"],
                    tracker["source_name"],
                    tracker["destination_name"],
                    inserted,
                )

            except Exception:
                logger.exception(
                    (
                        "Tracker %s "
                        "(%s → %s) failed"
                    ),
                    tracker["id"],
                    tracker["source_name"],
                    tracker["destination_name"],
                )

    logger.info("Collection cycle completed.")