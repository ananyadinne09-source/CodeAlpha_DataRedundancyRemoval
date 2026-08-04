"""
One-time migration script for the AI Duplicate Assistant feature.

Run this ONCE after pulling the updated code, if you already have an
existing instance/cadets.db with cadet records in it. It safely adds the
three new columns (is_duplicate, similarity_score, duplicate_of_id)
without deleting any existing data.

If you don't care about existing data, you can instead just delete
instance/cadets.db and let app.py recreate it from scratch on next run.

Usage:
    python migrate_db.py
"""

import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "cadets.db")


def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"No existing database found at {DB_PATH}.")
        print("Nothing to migrate — just run the app and it will be created fresh.")
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    added = []

    if not column_exists(cur, "records", "is_duplicate"):
        cur.execute(
            "ALTER TABLE records ADD COLUMN is_duplicate BOOLEAN NOT NULL DEFAULT 0"
        )
        added.append("is_duplicate")

    if not column_exists(cur, "records", "similarity_score"):
        cur.execute(
            "ALTER TABLE records ADD COLUMN similarity_score INTEGER"
        )
        added.append("similarity_score")

    if not column_exists(cur, "records", "duplicate_of_id"):
        cur.execute(
            "ALTER TABLE records ADD COLUMN duplicate_of_id INTEGER "
            "REFERENCES records(id)"
        )
        added.append("duplicate_of_id")

    con.commit()
    con.close()

    if added:
        print(f"Migration complete. Added columns: {', '.join(added)}")
    else:
        print("Database already up to date — no changes needed.")


if __name__ == "__main__":
    migrate()
