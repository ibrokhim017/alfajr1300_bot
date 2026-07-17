import hashlib
import sqlite3
from datetime import datetime
from typing import Optional

from config import DB_NAME


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER NOT NULL CHECK (amount > 0),
                sms TEXT NOT NULL,
                message_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
            """
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_created_at "
            "ON transactions(created_at)"
        )


def add_transaction(amount: int, sms: str) -> bool:
    message_hash = hashlib.sha256(sms.strip().encode("utf-8")).hexdigest()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with _connect() as db:
            db.execute(
                """
                INSERT INTO transactions (amount, sms, message_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (amount, sms.strip(), message_hash, created_at),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def get_total(days: Optional[int] = None) -> tuple[int, int]:
    query = "SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM transactions"
    values: tuple = ()

    if days is not None:
        query += " WHERE datetime(created_at) >= datetime('now', ?)"
        values = (f"-{days} days",)

    with _connect() as db:
        row = db.execute(query, values).fetchone()
    return int(row[0]), int(row[1])


def get_today_total() -> tuple[int, int]:
    with _connect() as db:
        row = db.execute(
            """
            SELECT COALESCE(SUM(amount), 0), COUNT(*)
            FROM transactions
            WHERE date(created_at) = date('now', 'localtime')
            """
        ).fetchone()
    return int(row[0]), int(row[1])
