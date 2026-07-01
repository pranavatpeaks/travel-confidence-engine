from __future__ import annotations

from datetime import UTC, datetime, timedelta

from db.database import connection


def _average_between(
    tracker_id: int,
    start: datetime,
    end: datetime,
) -> float | None:

    with connection() as conn:

        row = conn.execute(
            """
            SELECT AVG(fare) AS avg_fare
            FROM fare_observations
            WHERE tracker_id = ?
              AND observed_at BETWEEN ? AND ?
            """,
            (
                tracker_id,
                start.isoformat(),
                end.isoformat(),
            ),
        ).fetchone()

    if not row["avg_fare"]:
        return None

    return float(row["avg_fare"])


def get_latest_fare(
    tracker_id: int,
) -> int | None:

    with connection() as conn:

        row = conn.execute(
            """
            SELECT fare
            FROM fare_observations
            WHERE tracker_id = ?
            ORDER BY observed_at DESC
            LIMIT 1
            """,
            (tracker_id,),
        ).fetchone()

    if not row:
        return None

    return row["fare"]


def get_24h_average(
    tracker_id: int,
) -> float | None:

    end = datetime.now(UTC)

    start = end - timedelta(hours=24)

    return _average_between(
        tracker_id,
        start,
        end,
    )


def get_3d_average(
    tracker_id: int,
) -> float | None:

    end = datetime.now(UTC)

    start = end - timedelta(days=3)

    return _average_between(
        tracker_id,
        start,
        end,
    )


def get_7d_average(
    tracker_id: int,
) -> float | None:

    end = datetime.now(UTC)

    start = end - timedelta(days=7)

    return _average_between(
        tracker_id,
        start,
        end,
    )


def classify_trend(
    current: float,
    historical: float,
) -> str:

    if historical is None:
        return "UNKNOWN"

    difference = (
        current - historical
    ) / historical

    if difference >= 0.10:
        return "STRONGLY_RISING"

    if difference >= 0.03:
        return "RISING"

    if difference <= -0.10:
        return "STRONGLY_FALLING"

    if difference <= -0.03:
        return "FALLING"

    return "STABLE"


def get_trends(
    tracker_id: int,
) -> dict:

    current = get_latest_fare(
        tracker_id
    )

    if current is None:

        return {
            "current": None,
            "24h": None,
            "3d": None,
            "7d": None,
            "trend_24h": "UNKNOWN",
            "trend_3d": "UNKNOWN",
            "trend_7d": "UNKNOWN",
        }

    avg24 = get_24h_average(
        tracker_id
    )

    avg3 = get_3d_average(
        tracker_id
    )

    avg7 = get_7d_average(
        tracker_id
    )

    return {

        "current": current,

        "24h_average": avg24,

        "3d_average": avg3,

        "7d_average": avg7,

        "trend_24h": classify_trend(
            current,
            avg24,
        ),

        "trend_3d": classify_trend(
            current,
            avg3,
        ),

        "trend_7d": classify_trend(
            current,
            avg7,
        ),
    }