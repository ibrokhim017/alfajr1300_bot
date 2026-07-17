from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import re

from config import BOT_TOKEN, GROUP_ID
from database import init_db, add_transaction, get_today_total


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕌 Al Fajr Bot ishga tushdi!\n\n"
        "Buyruqlar:\n"
        "/today - Bugungi tushum"
    )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = get_today_total()

    await update.message.reply_text(
        f"📊 Bugungi tushum:\n\n💰 {total:,} so'm"
    )


async def save_sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return

    text = update.message.text or ""

    match = re.search(r'([\d\s]+)\s*so', text.lower())

    if not match:
        return

    amount = int(match.group(1).replace(" ", ""))

    add_transaction(amount, text)


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            save_sms,
        )
    )

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
