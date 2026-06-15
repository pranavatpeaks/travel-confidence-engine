from scrapers.redbus import RedBusScraper
from scrapers.city_mapper import get_city_id

from db.fare_repository import (
    insert_many_observations,
    count_observations,
)


def main() -> None:
    tracker_id = 3

    source_id = get_city_id("HYD")
    destination_id = get_city_id("BLR")

    print("=" * 80)
    print("Fetching fares from RedBus")
    print("=" * 80)

    with RedBusScraper(
        timeout=60,
        max_retries=1,
        limit=10,
    ) as scraper:

        observations = scraper.search(
            source_city_id=source_id,
            destination_city_id=destination_id,
            journey_date="2026-07-01",
        )

    print(f"Fetched {len(observations)} observations")

    inserted = insert_many_observations(
        tracker_id=tracker_id,
        observations=observations,
    )

    print(f"Inserted {inserted} rows")

    total = count_observations()

    print(f"Total observations in DB: {total}")


if __name__ == "__main__":
    main()