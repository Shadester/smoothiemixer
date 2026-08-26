import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.environ.get("DB_PATH", "smoothiemixer.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ingredients (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT    NOT NULL,
                category        TEXT    NOT NULL,
                unit_name       TEXT    NOT NULL,
                grams_per_unit  REAL    NOT NULL,
                calories_per_100g REAL  NOT NULL,
                in_stock        INTEGER NOT NULL DEFAULT 1
            )
        """)


def fix_implausible_calories() -> None:
    """Convert any calories_per_100g > 900 that are almost certainly raw kJ values.

    The highest real-food energy density is ~900 kcal/100 g (pure fat).  Values
    above that were stored as kJ (≈ 4.184×) due to the old lookup bug.
    """
    with db() as conn:
        conn.execute(
            "UPDATE ingredients "
            "SET calories_per_100g = ROUND(calories_per_100g / 4.184, 1) "
            "WHERE calories_per_100g > 900"
        )
