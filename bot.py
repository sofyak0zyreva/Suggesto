# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from handlers import add
from config import TOKEN


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Привет! Я бот для рекомендаций. Вот доступные команды:\n"
        "/add – добавить рекомендацию\n"
        "/rate – оценить рекомендацию\n"
        "/list – список рекомендаций\n"
        "/random – случайная рекомендация\n"
        "/help – помощь"
    )


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    add_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add.cmd_add)],
        states={
            add.CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.enter_category)],
            add.TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.enter_title)],
            add.AUTHOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.enter_author)],
            add.COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.enter_comment)],
            add.RATING: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.enter_rating)],
        },
        fallbacks=[],
    )
    application.add_handler(add_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
