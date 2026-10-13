
import sqlite3
from pathlib import Path

DB_PATH = Path("instance/campuslostfound.db")
BACKUP_PATH = Path("instance/campuslostfound_backup.db")

if not DB_PATH.exists():
    raise SystemExit("ERROR: Original database was not found.")

if not BACKUP_PATH.exists():
    raise SystemExit("ERROR: Database backup was not found.")

connection = sqlite3.connect(DB_PATH)

try:
    connection.execute("PRAGMA foreign_keys = OFF")

    # Check that all existing reports belong to registered users.
    for table in ("lost_item", "found_item"):
        invalid = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM {table} AS report
            LEFT JOIN user ON report.user_id = user.id
            WHERE user.id IS NULL
            """
        ).fetchone()[0]

        if invalid:
            raise RuntimeError(
                f"{table} contains {invalid} invalid user references."
            )

    connection.execute("BEGIN IMMEDIATE")

    for table in ("lost_item", "found_item"):
        temporary_table = f"{table}_new"

        connection.execute(f"""
            CREATE TABLE {temporary_table} (
                id INTEGER NOT NULL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                location VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                phone VARCHAR(20) NOT NULL,
                email VARCHAR(100) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)

        connection.execute(f"""
            INSERT INTO {temporary_table}
            (id, user_id, item_name, category, location,
             description, phone, email)
            SELECT id, user_id, item_name, category, location,
                   description, phone, email
            FROM {table}
        """)

        connection.execute(f"DROP TABLE {table}")
        connection.execute(
            f"ALTER TABLE {temporary_table} RENAME TO {table}"
        )

    connection.commit()

    connection.execute("PRAGMA foreign_keys = ON")

    integrity = connection.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    foreign_key_errors = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    print("Database migration completed.")
    print("Database integrity:", integrity)
    print("Foreign key errors:", foreign_key_errors)

    for table in ("user", "lost_item", "found_item"):
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        print(f"{table} records: {count}")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()