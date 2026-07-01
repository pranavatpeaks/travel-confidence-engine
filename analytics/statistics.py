from __future__ import annotations

import math
from statistics import median

from db.database import connection


def _get_fares(
    tracker_id: int,
) -> list[int]:

    with connection() as conn:

        rows = conn.execute(
            """
            SELECT fare
            FROM fare_observations
            WHERE tracker_id = ?
            ORDER BY observed_at
            """,
            (tracker_id,),
        ).fetchall()

    return [
        row["fare"]
        for row in rows
    ]


def _get_seats(
    tracker_id: int,
) -> list[int]:

    with connection() as conn:

        rows = conn.execute(
            """
            SELECT seats_available
            FROM fare_observations
            WHERE tracker_id = ?
            ORDER BY observed_at
            """,
            (tracker_id,),
        ).fetchall()

    return [
        row["seats_available"]
        for row in rows
    ]


def get_average_fare(
    tracker_id: int,
) -> float | None:

    fares = _get_fares(tracker_id)

    if not fares:
        return None

    return round(
        sum(fares) / len(fares),
        2,
    )


def get_median_fare(
    tracker_id: int,
) -> float | None:

    fares = _get_fares(tracker_id)

    if not fares:
        return None

    return float(
        median(fares)
    )


def get_lowest_fare(
    tracker_id: int,
) -> int | None:

    fares = _get_fares(tracker_id)

    if not fares:
        return None

    return min(fares)


def get_highest_fare(
    tracker_id: int,
) -> int | None:

    fares = _get_fares(tracker_id)

    if not fares:
        return None

    return max(fares)


def get_price_range(
    tracker_id: int,
) -> int | None:

    fares = _get_fares(tracker_id)

    if not fares:
        return None

    return (
        max(fares)
        - min(fares)
    )


def get_standard_deviation(
    tracker_id: int,
) -> float | None:

    fares = _get_fares(tracker_id)

    if len(fares) < 2:
        return None

    mean = (
        sum(fares)
        / len(fares)
    )

    variance = sum(
        (
            fare - mean
        ) ** 2
        for fare in fares
    ) / len(fares)

    return round(
        math.sqrt(variance),
        2,
    )


def get_average_seats(
    tracker_id: int,
) -> float | None:

    seats = _get_seats(
        tracker_id
    )

    if not seats:
        return None

    return round(
        sum(seats) / len(seats),
        2,
    )


def get_observation_count(
    tracker_id: int,
) -> int:

    fares = _get_fares(
        tracker_id
    )

    return len(fares)


def get_current_percentile(
    tracker_id: int,
    current_fare: int,
) -> float | None:

    fares = _get_fares(
        tracker_id
    )

    if not fares:
        return None

    cheaper = sum(
        1
        for fare in fares
        if fare <= current_fare
    )

    return round(
        (
            cheaper
            / len(fares)
        )
        * 100,
        2,
    )


def get_statistics(
    tracker_id: int,
    current_fare: int,
) -> dict:

    return {

        "average_fare":
            get_average_fare(
                tracker_id
            ),

        "median_fare":
            get_median_fare(
                tracker_id
            ),

        "lowest_fare":
            get_lowest_fare(
                tracker_id
            ),

        "highest_fare":
            get_highest_fare(
                tracker_id
            ),

        "price_range":
            get_price_range(
                tracker_id
            ),

        "std_deviation":
            get_standard_deviation(
                tracker_id
            ),

        "average_seats":
            get_average_seats(
                tracker_id
            ),

        "observations":
            get_observation_count(
                tracker_id
            ),

        "percentile":
            get_current_percentile(
                tracker_id,
                current_fare,
            ),
    }