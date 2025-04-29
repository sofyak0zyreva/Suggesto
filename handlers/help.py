from telegram import Update
from telegram.ext import CallbackContext


async def cmd_help(update: Update, context: CallbackContext) -> None:
    help_text = (
        "🤖 Привет! Вот что я умею:\n"
        "🔹 Добавить рекомендацию → /add\n"
        "🔹 Оценить что-то → /rate\n"
        "🔹 Посмотреть список рекомендаций → /list\n"
        "🔹 Получить случайную рекомендацию → /random"
    )
    await update.message.reply_text(help_text)
