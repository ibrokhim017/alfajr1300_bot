import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROUP_ID = int(os.getenv("GROUP_ID", "0"))
DB_NAME = os.getenv("DB_NAME", "database.db")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set.")

if not GROUP_ID:
    raise RuntimeError("GROUP_ID environment variable is not set.")
