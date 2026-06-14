from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path("travel_confidence.db")


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


@contextmanager
def connection(db_path: str | None = None):
    conn = get_connection(db_path)

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def initialize_database() -> None:
    from db.models import create_tables

    create_tables()