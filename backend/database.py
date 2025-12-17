import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "sparklets.sqlite"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sparklets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_filename TEXT NOT NULL,
                to_name TEXT NOT NULL,
                from_name TEXT NOT NULL,
                message TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                background_color TEXT NOT NULL,
                card_color TEXT NOT NULL,
                text_color TEXT NOT NULL,
                card_rotation INTEGER DEFAULT 5,
                image_offset_x REAL DEFAULT 0,
                image_offset_y REAL DEFAULT 0,
                image_scale REAL DEFAULT 1
            )
        """)
        conn.commit()

        # Migration: Add card_rotation column if it doesn't exist
        try:
            conn.execute("ALTER TABLE sparklets ADD COLUMN card_rotation INTEGER DEFAULT 5")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Migration: Add image position columns if they don't exist
        try:
            conn.execute("ALTER TABLE sparklets ADD COLUMN image_offset_x REAL DEFAULT 0")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE sparklets ADD COLUMN image_offset_y REAL DEFAULT 0")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE sparklets ADD COLUMN image_scale REAL DEFAULT 1")
            conn.commit()
        except sqlite3.OperationalError:
            pass
