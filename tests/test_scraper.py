from scrapers.redbus import RedBusScraper
from scrapers.city_mapper import get_city_id


def main() -> None:
    source = "HYD"
    destination = "BLR"
    journey_date = "2026-07-01"

    source_id = get_city_id(source)
    destination_id = get_city_id(destination)

    print("=" * 80)
    print(f"Route: {source} -> {destination}")
    print(f"Date : {journey_date}")
    print(f"Source ID      : {source_id}")
    print(f"Destination ID : {destination_id}")
    print("=" * 80)

    try:
        with RedBusScraper(
            timeout=60,
            max_retries=1,
            limit=10,
        ) as scraper:

            observations = scraper.search(
                source_city_id=source_id,
                destination_city_id=destination_id,
                journey_date=journey_date,
            )

        print(f"\nFound {len(observations)} buses\n")

        if not observations:
            print("No buses found.")
            return

        print("-" * 80)
        print("Top 10 Cheapest Buses")
        print("-" * 80)

        for idx, obs in enumerate(observations[:10], start=1):
            print(
                f"{idx:02d}. "
                f"{obs.operator:<40} "
                f"₹{obs.fare:<6} "
                f"Seats: {obs.seats_available}"
            )

        cheapest = observations[0]

        print("\n" + "=" * 80)
        print("CHEAPEST OPTION")
        print("=" * 80)

        print(f"Operator : {cheapest.operator}")
        print(f"Fare     : ₹{cheapest.fare}")
        print(f"Seats    : {cheapest.seats_available}")
        print(f"Platform : {cheapest.platform}")
        print(f"Observed : {cheapest.observed_at}")

    except Exception as exc:
        print("\nERROR")
        print("=" * 80)
        print(type(exc).__name__)
        print(exc)


if __name__ == "__main__":
    main()