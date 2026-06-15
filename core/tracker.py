from __future__ import annotations

from typing import Any

from db.database import connection


def create_tracker(
    chat_id: str,

    source_name: str,
    source_id: int,

    destination_name: str,
    destination_id: int,

    journey_date: str,
) -> dict[str, Any]:
    """
    Create a tracker.

    If the same tracker already exists but is inactive,
    reactivate it instead of creating a new row.
    """

    with connection() as conn:

        existing = conn.execute(
            """
            SELECT *
            FROM trackers
            WHERE chat_id = ?
              AND source_name = ?
              AND destination_name = ?
              AND journey_date = ?
            """,
            (
                chat_id,
                source_name,
                destination_name,
                journey_date,
            ),
        ).fetchone()

        if existing:

            if existing["active"] == 0:

                conn.execute(
                    """
                    UPDATE trackers
                    SET active = 1
                    WHERE id = ?
                    """,
                    (
                        existing["id"],
                    ),
                )

                row = conn.execute(
                    """
                    SELECT *
                    FROM trackers
                    WHERE id = ?
                    """,
                    (
                        existing["id"],
                    ),
                ).fetchone()

                return dict(row)

            raise ValueError(
                "Tracker already exists and is active."
            )

        cursor = conn.execute(
            """
            INSERT INTO trackers (
                    chat_id,
                    source_name,
                    source_id,
                    destination_name,
                    destination_id,
                    journey_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                chat_id,
                source_name,
                source_id,
                destination_name,
                destination_id,
                journey_date,
            ),
        )

        tracker_id = cursor.lastrowid

        row = conn.execute(
            """
            SELECT *
            FROM trackers
            WHERE id = ?
            """,
            (
                tracker_id,
            ),
        ).fetchone()

    return dict(row)

def get_active_trackers(
    chat_id: str,
) -> list[dict[str, Any]]:

    with connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM trackers
            WHERE chat_id = ?
              AND active = 1
            ORDER BY created_at DESC
            """,
            (chat_id,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_all_active_trackers() -> list[dict[str, Any]]:
    """
    Used by the orchestrator.

    Returns every active tracker in the system.
    """

    with connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM trackers
            WHERE active = 1
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def deactivate_tracker(
    tracker_id: int,
    chat_id: str,
) -> bool:

    with connection() as conn:
        cursor = conn.execute(
            """
            UPDATE trackers
            SET active = 0
            WHERE id = ?
              AND chat_id = ?
              AND active = 1
            """,
            (
                tracker_id,
                chat_id,
            ),
        )

    return cursor.rowcount > 0


def get_tracker_by_id(
    tracker_id: int,
    chat_id: str,
) -> dict[str, Any] | None:

    with connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM trackers
            WHERE id = ?
              AND chat_id = ?
            """,
            (
                tracker_id,
                chat_id,
            ),
        ).fetchone()

    return dict(row) if row else None