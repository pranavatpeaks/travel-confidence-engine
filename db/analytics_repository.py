from __future__ import annotations

from db.database import connection


def get_tracker_summary(
    tracker_id: int,
) -> dict | None:

    with connection() as conn:

        row = conn.execute(
            """
            SELECT
                MIN(fare) AS lowest_fare,
                MAX(fare) AS highest_fare,
                COUNT(*) AS observations
            FROM fare_observations
            WHERE tracker_id = ?
            """,
            (tracker_id,),
        ).fetchone()

        latest = conn.execute(
            """
            SELECT *
            FROM fare_observations
            WHERE tracker_id = ?
            ORDER BY observed_at DESC
            LIMIT 1
            """,
            (tracker_id,),
        ).fetchone()

    if not latest:
        return None

    return {
        "lowest_fare": row["lowest_fare"],
        "highest_fare": row["highest_fare"],
        "observations": row["observations"],
        "latest_fare": latest["fare"],
        "latest_operator": latest["operator"],
        "latest_seats": latest["seats_available"],
        "latest_observed_at": latest["observed_at"],
    }