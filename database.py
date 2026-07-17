import sqlite3

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount INTEGER,
        sms TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def add_transaction(amount, sms):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO transactions (amount, sms) VALUES (?, ?)",
        (amount, sms)
    )

    conn.commit()
    conn.close()

def get_today_total():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount),0)
        FROM transactions
        WHERE date(created_at)=date('now','localtime')
    """)

    total = cursor.fetchone()[0]
    conn.close()

    return total
