from __future__ import annotations

from typing import Iterable

from db.database import connection
from scrapers.models import FareObservation


def insert_fare_observation(
    tracker_id: int,
    observation: FareObservation,
) -> int:

    with connection() as conn:

        cursor = conn.execute(
            """
            INSERT INTO fare_observations (
                tracker_id,
                platform,
                operator,
                bus_type,
                is_ac,
                is_sleeper,
                departure_time,
                arrival_time,
                journey_duration_min,
                fare,
                seats_available,
                observed_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                tracker_id,
                observation.platform,
                observation.operator,

                observation.bus_type,
                int(observation.is_ac),
                int(observation.is_sleeper),

                observation.departure_time,
                observation.arrival_time,
                observation.journey_duration_min,

                observation.fare,
                observation.seats_available,

                observation.observed_at.isoformat(),
            ),
        )

        return int(
            cursor.lastrowid
        )


def insert_many_observations(
    tracker_id: int,
    observations: Iterable[FareObservation],
) -> int:

    rows = [
        (
            tracker_id,

            obs.platform,
            obs.operator,

            obs.bus_type,
            int(obs.is_ac),
            int(obs.is_sleeper),

            obs.departure_time,
            obs.arrival_time,
            obs.journey_duration_min,

            obs.fare,
            obs.seats_available,

            obs.observed_at.isoformat(),
        )
        for obs in observations
    ]

    if not rows:
        return 0

    with connection() as conn:

        conn.executemany(
            """
            INSERT INTO fare_observations (
                tracker_id,
                platform,
                operator,
                bus_type,
                is_ac,
                is_sleeper,
                departure_time,
                arrival_time,
                journey_duration_min,
                fare,
                seats_available,
                observed_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            rows,
        )

    return len(rows)


def count_observations() -> int:

    with connection() as conn:

        row = conn.execute(
            """
            SELECT COUNT(*)
            FROM fare_observations
            """
        ).fetchone()

    return int(
        row[0]
    )


def get_latest_observations(
    tracker_id: int,
    limit: int = 20,
) -> list[dict]:

    with connection() as conn:

        rows = conn.execute(
            """
            SELECT *
            FROM fare_observations
            WHERE tracker_id = ?
            ORDER BY observed_at DESC
            LIMIT ?
            """,
            (
                tracker_id,
                limit,
            ),
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def get_latest_fare_for_tracker(
    tracker_id: int,
) -> dict | None:

    with connection() as conn:

        row = conn.execute(
            """
            SELECT *
            FROM fare_observations
            WHERE tracker_id = ?
            ORDER BY observed_at DESC
            LIMIT 1
            """,
            (
                tracker_id,
            ),
        ).fetchone()

    return (
        dict(row)
        if row
        else None
    )


def get_lowest_fare_for_tracker(
    tracker_id: int,
) -> dict | None:

    with connection() as conn:

        row = conn.execute(
            """
            SELECT *
            FROM fare_observations
            WHERE tracker_id = ?
            ORDER BY fare ASC
            LIMIT 1
            """,
            (
                tracker_id,
            ),
        ).fetchone()

    return (
        dict(row)
        if row
        else None
    )


def get_tracker_statistics(
    tracker_id: int,
) -> dict:

    with connection() as conn:

        stats = conn.execute(
            """
            SELECT
                MIN(fare) AS lowest_fare,
                MAX(fare) AS highest_fare,
                COUNT(*) AS observations
            FROM fare_observations
            WHERE tracker_id = ?
            """,
            (
                tracker_id,
            ),
        ).fetchone()

        latest = conn.execute(
            """
            SELECT
                fare,
                operator,
                bus_type,
                departure_time,
                arrival_time,
                journey_duration_min,
                seats_available,
                observed_at
            FROM fare_observations
            WHERE tracker_id = ?
            ORDER BY observed_at DESC
            LIMIT 1
            """,
            (
                tracker_id,
            ),
        ).fetchone()

    return {
        "lowest_fare": stats["lowest_fare"],
        "highest_fare": stats["highest_fare"],
        "observations": stats["observations"],

        "latest_fare":
            latest["fare"]
            if latest
            else None,

        "latest_operator":
            latest["operator"]
            if latest
            else None,

        "latest_bus_type":
            latest["bus_type"]
            if latest
            else None,

        "latest_departure_time":
            latest["departure_time"]
            if latest
            else None,

        "latest_arrival_time":
            latest["arrival_time"]
            if latest
            else None,

        "latest_duration":
            latest["journey_duration_min"]
            if latest
            else None,

        "latest_seats":
            latest["seats_available"]
            if latest
            else None,

        "latest_observed_at":
            latest["observed_at"]
            if latest
            else None,
    }


def get_cheapest_options_for_tracker(
    tracker_id: int,
    limit: int = 3,
) -> list[dict]:

    with connection() as conn:

        latest_timestamp = conn.execute(
            """
            SELECT MAX(observed_at)
            FROM fare_observations
            WHERE tracker_id = ?
            """,
            (
                tracker_id,
            ),
        ).fetchone()[0]

        if not latest_timestamp:
            return []

        rows = conn.execute(
            """
            SELECT *
            FROM fare_observations
            WHERE tracker_id = ?
              AND observed_at = ?
            ORDER BY fare ASC
            LIMIT ?
            """,
            (
                tracker_id,
                latest_timestamp,
                limit,
            ),
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]