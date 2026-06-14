from __future__ import annotations

from typing import Any

from db.database import connection


def create_tracker(
    chat_id: str,
    source: str,
    destination: str,
    journey_date: str,
) -> dict[str, Any]:
    """
    Create a new tracker and return the created record.
    """

    with connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO trackers (
                chat_id,
                source,
                destination,
                journey_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                chat_id,
                source,
                destination,
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
            (tracker_id,),
        ).fetchone()

    return dict(row)


def get_active_trackers(
    chat_id: str,
) -> list[dict[str, Any]]:
    """
    Return all active trackers for a Telegram user.
    """

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


def deactivate_tracker(
    tracker_id: int,
    chat_id: str,
) -> bool:
    """
    Deactivate a tracker belonging to a user.

    Returns:
        True if tracker was found and deactivated.
        False otherwise.
    """

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
    """
    Fetch a single tracker.
    """

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