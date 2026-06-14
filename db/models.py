from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from db.database import connection, get_connection

logger = logging.getLogger(__name__)

# ── DDL ───────────────────────────────────────────────────────────────────────

_CREATE_TRACKERS = """
CREATE TABLE IF NOT EXISTS trackers (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    chat_id       TEXT     NOT NULL,
    source        TEXT     NOT NULL,
    destination   TEXT     NOT NULL,
    journey_date  TEXT     NOT NULL,            -- stored as YYYY-MM-DD
    active        INTEGER  NOT NULL DEFAULT 1,  -- 1 = active, 0 = stopped
    created_at    TEXT     NOT NULL
                           DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE (chat_id, source, destination, journey_date)
);
"""

_CREATE_IDX_CHAT_ACTIVE = """
CREATE INDEX IF NOT EXISTS idx_trackers_chat_active
    ON trackers (chat_id, active);
"""

_CREATE_IDX_JOURNEY_DATE = """
CREATE INDEX IF NOT EXISTS idx_trackers_journey_date
    ON trackers (journey_date);
"""


# ── Dataclass model ───────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Tracker:
    """In-memory representation of a row from the ``trackers`` table.

    All fields map 1-to-1 to database columns.  ``id`` and ``created_at``
    are ``None`` before the row has been persisted.
    """

    chat_id: str
    source: str
    destination: str
    journey_date: date
    active: bool = True
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    # ── Factories ─────────────────────────────────────────────────────────────

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Tracker:
        """Construct a ``Tracker`` from a ``sqlite3.Row`` (column-name access).

        Args:
            row: A row returned from a query against the ``trackers`` table.

        Returns:
            A fully populated ``Tracker`` instance.
        """
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

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def route_label(self) -> str:
        """Human-readable route string, e.g. ``'HYD → BLR'``."""
        return f"{self.source} → {self.destination}"


# ── Table creation ────────────────────────────────────────────────────────────

def create_tables(db_path: str | None = None) -> None:
    """Create the ``trackers`` table and its indexes if they do not exist.

    Idempotent — safe to call on every application startup without risk of
    data loss or duplicate schema objects.

    Args:
        db_path: Optional path to the SQLite file.  When ``None`` the default
                 path configured in ``database.py`` is used.  Pass
                 ``':memory:'`` in tests.
    """
    kwargs = {"db_path": db_path} if db_path is not None else {}

    logger.info("Creating tables (if not exist).")
    with connection(**kwargs) as conn:
        conn.execute(_CREATE_TRACKERS)
        conn.execute(_CREATE_IDX_CHAT_ACTIVE)
        conn.execute(_CREATE_IDX_JOURNEY_DATE)

    logger.info("Table 'trackers' and indexes are ready.")