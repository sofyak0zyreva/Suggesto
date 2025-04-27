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
        "/list – посмотри список рекомендаций\n"
        "/random – случайная рекомендация\n"
        "/help – помощь"
    )


def main():
    application = Application.builder().token(TOKEN).build()

    # Определение обработчиков команд
    application.add_handler(CommandHandler("start", start))

    # Добавление обработчика добавления рекомендаций
    add_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add.cmd_add)],
        states={
            "CATEGORY": [MessageHandler(filters.TEXT, add.enter_category)],
            "TITLE": [MessageHandler(filters.TEXT, add.enter_title)],
            "AUTHOR": [MessageHandler(filters.TEXT, add.enter_author)],
            "COMMENT": [MessageHandler(filters.TEXT, add.enter_comment)],
            "RATING": [MessageHandler(filters.TEXT, add.enter_rating)]
        },
        fallbacks=[]
    )

    # Регистрируем обработчики
    application.add_handler(add_handler)

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()
