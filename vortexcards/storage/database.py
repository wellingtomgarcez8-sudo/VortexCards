from __future__ import annotations
import sqlite3
from pathlib import Path
from platformdirs import user_data_dir

APP_DIR = Path(user_data_dir("VortexCards", "VortexCards"))
DB_PATH = APP_DIR / "vortexcards.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT UNIQUE NOT NULL,
 password_hash TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS stats(
 username TEXT PRIMARY KEY,
 games INTEGER NOT NULL DEFAULT 0,
 wins INTEGER NOT NULL DEFAULT 0,
 losses INTEGER NOT NULL DEFAULT 0,
 play_seconds INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS history(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT NOT NULL,
 played_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 mode TEXT NOT NULL,
 result TEXT NOT NULL,
 score INTEGER NOT NULL DEFAULT 0
);
"""

def connect():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
