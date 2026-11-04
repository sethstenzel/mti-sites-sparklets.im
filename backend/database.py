import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "sparklets.sqlite"

# Columns added after the original schema: (name, definition)
MIGRATIONS = [
    ("card_rotation", "INTEGER DEFAULT 5"),
    ("image_offset_x", "REAL DEFAULT 0"),
    ("image_offset_y", "REAL DEFAULT 0"),
    ("image_scale", "REAL DEFAULT 1"),
    ("entry_animation", "TEXT DEFAULT 'drop'"),
]


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
                image_scale REAL DEFAULT 1,
                entry_animation TEXT DEFAULT 'drop'
            )
        """)
        existing = {row["name"] for row in conn.execute("PRAGMA table_info(sparklets)")}
        for name, definition in MIGRATIONS:
            if name not in existing:
                conn.execute(f"ALTER TABLE sparklets ADD COLUMN {name} {definition}")
        conn.commit()
