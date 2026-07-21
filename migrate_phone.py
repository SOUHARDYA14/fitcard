"""One-off migration: add phone number support for OTP login.
Safe to re-run.
"""
import sqlite3

conn = sqlite3.connect("credit_cards.db")
existing = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
if "phone" not in existing:
    # SQLite's ALTER TABLE ADD COLUMN can't carry a UNIQUE constraint,
    # so enforce uniqueness with a separate partial index instead.
    conn.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    print("Added users.phone")
else:
    print("users.phone already exists")
conn.execute(
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_phone ON users(phone) WHERE phone IS NOT NULL"
)
conn.commit()
conn.close()
