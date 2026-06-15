from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from db.database import connection

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# TRACKERS TABLE
# ──────────────────────────────────────────────────────────────────────────────

_CREATE_TRACKERS = """
CREATE TABLE IF NOT EXISTS trackers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    chat_id TEXT NOT NULL,

    source_name TEXT NOT NULL,
    source_id INTEGER NOT NULL,

    destination_name TEXT NOT NULL,
    destination_id INTEGER NOT NULL,

    journey_date TEXT NOT NULL,

    active INTEGER NOT NULL DEFAULT 1,

    created_at TEXT NOT NULL DEFAULT (
        STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'NOW')
    )
);
"""

_CREATE_IDX_CHAT_ACTIVE = """
CREATE INDEX IF NOT EXISTS idx_trackers_chat_active
ON trackers(chat_id, active);
"""

_CREATE_IDX_JOURNEY_DATE = """
CREATE INDEX IF NOT EXISTS idx_trackers_journey_date
ON trackers(journey_date);
"""


# ──────────────────────────────────────────────────────────────────────────────
# FARE OBSERVATIONS TABLE
# ──────────────────────────────────────────────────────────────────────────────

_CREATE_FARE_OBSERVATIONS = """
CREATE TABLE IF NOT EXISTS fare_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tracker_id INTEGER NOT NULL,

    platform TEXT NOT NULL,

    operator TEXT NOT NULL,

    bus_type TEXT NOT NULL,

    is_ac INTEGER NOT NULL,

    is_sleeper INTEGER NOT NULL,

    departure_time TEXT,

    arrival_time TEXT,

    journey_duration_min INTEGER,

    fare INTEGER NOT NULL,

    seats_available INTEGER NOT NULL,

    observed_at TEXT NOT NULL,

    FOREIGN KEY (tracker_id)
        REFERENCES trackers(id)
);
"""

_CREATE_IDX_FARE_TRACKER_ID = """
CREATE INDEX IF NOT EXISTS idx_fare_tracker_id
ON fare_observations(tracker_id);
"""

_CREATE_IDX_FARE_OBSERVED_AT = """
CREATE INDEX IF NOT EXISTS idx_fare_observed_at
ON fare_observations(observed_at);
"""


# ──────────────────────────────────────────────────────────────────────────────
# TRACKER MODEL
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Tracker:
    chat_id: str

    source_name: str
    source_id: int

    destination_name: str
    destination_id: int

    journey_date: str

    active: bool = True

    id: Optional[int] = None

    created_at: Optional[datetime] = None

    @classmethod
    def from_row(
        cls,
        row: sqlite3.Row,
    ) -> "Tracker":

        return cls(
            id=row["id"],
            chat_id=row["chat_id"],

            source_name=row["source_name"],
            source_id=row["source_id"],

            destination_name=row["destination_name"],
            destination_id=row["destination_id"],

            journey_date=row["journey_date"],

            active=bool(row["active"]),

            created_at=(
                datetime.fromisoformat(
                    row["created_at"]
                )
                if row["created_at"]
                else None
            ),
        )

    @property
    def route_label(self) -> str:

        return (
            f"{self.source_name} → "
            f"{self.destination_name}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# MIGRATIONS
# ──────────────────────────────────────────────────────────────────────────────

def _ensure_column(
    conn,
    column_name: str,
    definition: str,
) -> None:

    columns = conn.execute(
        """
        PRAGMA table_info(
            fare_observations
        )
        """
    ).fetchall()

    existing = {
        row[1]
        for row in columns
    }

    if column_name not in existing:

        logger.info(
            "Adding column: %s",
            column_name,
        )

        conn.execute(
            f"""
            ALTER TABLE fare_observations
            ADD COLUMN {column_name}
            {definition}
            """
        )


# ──────────────────────────────────────────────────────────────────────────────
# TABLE CREATION
# ──────────────────────────────────────────────────────────────────────────────

def create_tables(
    db_path: str | None = None,
) -> None:

    kwargs = (
        {"db_path": db_path}
        if db_path is not None
        else {}
    )

    logger.info(
        "Creating tables (if not exist)."
    )

    with connection(**kwargs) as conn:

        conn.execute(
            _CREATE_TRACKERS
        )

        conn.execute(
            _CREATE_IDX_CHAT_ACTIVE
        )

        conn.execute(
            _CREATE_IDX_JOURNEY_DATE
        )

        conn.execute(
            _CREATE_FARE_OBSERVATIONS
        )

        conn.execute(
            _CREATE_IDX_FARE_TRACKER_ID
        )

        conn.execute(
            _CREATE_IDX_FARE_OBSERVED_AT
        )

        _ensure_column(
            conn,
            "departure_time",
            "TEXT",
        )

        _ensure_column(
            conn,
            "arrival_time",
            "TEXT",
        )

        _ensure_column(
            conn,
            "journey_duration_min",
            "INTEGER",
        )

    logger.info(
        "Database tables ready."
    )