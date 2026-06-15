from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
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

    created_at TEXT NOT NULL
        DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

    UNIQUE(
        chat_id,
        source_name,
        destination_name,
        journey_date
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
    journey_date: date
    active: bool = True
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Tracker":
        return cls(
            id=row["id"],
            chat_id=row["chat_id"],
            source=row["source"],
            destination=row["destination"],
            journey_date=date.fromisoformat(row["journey_date"]),
            active=bool(row["active"]),
            created_at=(
                datetime.fromisoformat(row["created_at"])
                if row["created_at"]
                else None
            ),
        )

    @property
    def route_label(self) -> str:
        return f"{self.source} → {self.destination}"


# ──────────────────────────────────────────────────────────────────────────────
# TABLE CREATION
# ──────────────────────────────────────────────────────────────────────────────

def create_tables(db_path: str | None = None) -> None:
    kwargs = {"db_path": db_path} if db_path is not None else {}

    logger.info("Creating tables (if not exist).")

    with connection(**kwargs) as conn:
        conn.execute(_CREATE_TRACKERS)
        conn.execute(_CREATE_IDX_CHAT_ACTIVE)
        conn.execute(_CREATE_IDX_JOURNEY_DATE)

        conn.execute(_CREATE_FARE_OBSERVATIONS)
        conn.execute(_CREATE_IDX_FARE_TRACKER_ID)
        conn.execute(_CREATE_IDX_FARE_OBSERVED_AT)

    logger.info("Database tables ready.")