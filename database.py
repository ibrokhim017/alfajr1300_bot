import aiosqlite

DB_NAME = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount INTEGER NOT NULL,
            sms TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        await db.commit()

async def add_transaction(amount, sms):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO transactions (amount, sms) VALUES (?, ?)",
            (amount, sms)
        )
        await db.commit()

async def get_today_total():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT COALESCE(SUM(amount),0)
            FROM transactions
            WHERE date(created_at)=date('now','localtime')
        """)
        row = await cursor.fetchone()
        return row[0]
