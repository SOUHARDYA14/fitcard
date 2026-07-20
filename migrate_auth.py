"""One-off migration: add auth + saved-recommendation tables to credit_cards.db.
Safe to re-run (CREATE TABLE IF NOT EXISTS).
"""
import sqlite3

conn = sqlite3.connect("credit_cards.db")
conn.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,              -- NULL for OAuth-only accounts
    name TEXT,
    google_sub TEXT UNIQUE,          -- Google's stable account id, NULL if never used Google login
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS saved_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    inputs_json TEXT NOT NULL,       -- the full parameter form the user submitted
    results_json TEXT NOT NULL,      -- the top-5 result snapshot at that time
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
""")
conn.commit()
conn.close()
print("Auth tables ready.")
