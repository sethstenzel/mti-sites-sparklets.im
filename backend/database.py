import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "sparklets.sqlite"

SCHEMA = """
-- One row per sparklet. `id` is internal only and never leaves the server;
-- clients only ever see `public_id`, a random 128-bit URL-safe token.
CREATE TABLE IF NOT EXISTS sparklets (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    public_id        TEXT    NOT NULL UNIQUE,
    to_name          TEXT    NOT NULL,
    from_name        TEXT    NOT NULL,
    message          TEXT    NOT NULL,
    image_filename   TEXT    NOT NULL,
    background_color TEXT    NOT NULL,
    card_color       TEXT    NOT NULL,
    text_color       TEXT    NOT NULL,
    card_rotation    INTEGER NOT NULL DEFAULT 5,
    entry_animation  TEXT    NOT NULL DEFAULT 'drop',
    font             TEXT    NOT NULL DEFAULT 'kalam',
    -- Access control (prepared for the future user system):
    --   'public'     -> anyone with the link can view (the only mode used today)
    --   'restricted' -> viewer must be signed in AND appear in sparklet_access
    visibility       TEXT    NOT NULL DEFAULT 'public'
                     CHECK (visibility IN ('public', 'restricted')),
    -- Creator's account once users exist; NULL for anonymous sparklets.
    owner_user_id    INTEGER,
    created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sparklets_owner ON sparklets(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_sparklets_created ON sparklets(created_at);

-- Who a restricted sparklet is shared with. A grant targets an account (user_id)
-- or, before that person has signed up, an invited email address.
-- Not used yet; created now so the user system can plug straight in.
CREATE TABLE IF NOT EXISTS sparklet_access (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sparklet_id INTEGER NOT NULL REFERENCES sparklets(id) ON DELETE CASCADE,
    user_id     INTEGER,
    email       TEXT COLLATE NOCASE,
    role        TEXT    NOT NULL DEFAULT 'viewer' CHECK (role IN ('viewer', 'editor')),
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (user_id IS NOT NULL OR email IS NOT NULL),
    UNIQUE (sparklet_id, user_id),
    UNIQUE (sparklet_id, email)
);

CREATE INDEX IF NOT EXISTS idx_access_user ON sparklet_access(user_id);
CREATE INDEX IF NOT EXISTS idx_access_email ON sparklet_access(email);
"""


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(sparklets)")}
        if columns and "public_id" not in columns:
            # Never silently drop data: the old numeric-id schema must be archived by hand.
            raise RuntimeError(
                f"{DB_PATH} uses the old sparklets schema (numeric ids). "
                "Move it to a backup location and restart to create a fresh database."
            )
        conn.executescript(SCHEMA)
        conn.commit()
