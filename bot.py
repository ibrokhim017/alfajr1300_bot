import logging
import re

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN, GROUP_ID
from database import add_transaction, get_today_total, get_total, init_db

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
# HTTP request logs include the bot token in the request URL, so keep them hidden.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

CREDIT_WORDS = (
    "tushdi",
    "tushum",
    "kirim",
    "qabul qilindi",
    "hisobingizga",
    "zachislen",
    "зачислен",
    "поступил",
)
DEBIT_WORDS = (
    "yechildi",
    "yechib olindi",
    "chiqim",
    "to'lov",
    "to‘lov",
    "oplata",
    "оплата",
    "spisan",
    "списан",
)
AMOUNT_PATTERN = re.compile(
    r"(?<!\d)(\d[\d\s,\.]*\d|\d)\s*(?:so['‘’]?m|uzs|сум)",
    re.IGNORECASE,
)


def format_money(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " so'm"


def is_allowed_chat(update: Update) -> bool:
    return bool(update.effective_chat and update.effective_chat.id == GROUP_ID)


async def send_report(
    update: Update,
    title: str,
    total: int,
    count: int,
) -> None:
    await update.effective_message.reply_text(
        f"📊 {title}\n\n💰 {format_money(total)}\n🧾 Tranzaksiyalar: {count} ta"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed_chat(update):
        return
    await update.effective_message.reply_text(
        "🕌 Al Fajr bot ishga tushdi.\n\n"
        "/today — bugungi tushum\n"
        "/week — so‘nggi 7 kun\n"
        "/month — so‘nggi 30 kun\n"
        "/stats — umumiy statistika\n"
        "/help — yordam"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_allowed_chat(update):
        total, count = get_today_total()
        await send_report(update, "Bugungi tushum", total, count)


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_allowed_chat(update):
        total, count = get_total(days=7)
        await send_report(update, "So‘nggi 7 kun tushumi", total, count)


async def month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_allowed_chat(update):
        total, count = get_total(days=30)
        await send_report(update, "So‘nggi 30 kun tushumi", total, count)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_allowed_chat(update):
        total, count = get_total()
        await send_report(update, "Umumiy tushum", total, count)


def extract_amount(text: str) -> int | None:
    normalized = text.lower()
    if any(word in normalized for word in DEBIT_WORDS):
        return None
    is_credit = any(word in normalized for word in CREDIT_WORDS)
    is_uzqr_payment = "uzqr" in normalized and "new qr" in normalized
    if not is_credit and not is_uzqr_payment:
        return None

    match = AMOUNT_PATTERN.search(normalized)
    if not match:
        return None

    digits = re.sub(r"\D", "", match.group(1))
    if not digits:
        return None
    return int(digits)


async def save_sms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed_chat(update) or not update.effective_message:
        return

    text = update.effective_message.text or update.effective_message.caption or ""
    amount = extract_amount(text)
    if amount is None:
        return

    if add_transaction(amount, text):
        logger.info("Saved income: %s", amount)
    else:
        logger.info("Skipped duplicate message")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)


def main() -> None:
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()
    group_commands = filters.Chat(chat_id=GROUP_ID)

    app.add_handler(CommandHandler("start", start, filters=group_commands))
    app.add_handler(CommandHandler("help", help_command, filters=group_commands))
    app.add_handler(CommandHandler("today", today, filters=group_commands))
    app.add_handler(CommandHandler("week", week, filters=group_commands))
    app.add_handler(CommandHandler("month", month, filters=group_commands))
    app.add_handler(CommandHandler("stats", stats, filters=group_commands))
    app.add_handler(
        MessageHandler(
            filters.Chat(chat_id=GROUP_ID) & filters.ALL & ~filters.COMMAND,
            save_sms,
        )
    )
    app.add_error_handler(error_handler)

    logger.info("Al Fajr bot started for group %s", GROUP_ID)
    app.run_polling(drop_pending_updates=False)


if __name__ == "__main__":
    main()
