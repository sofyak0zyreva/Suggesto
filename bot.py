# bot.py
from handlers import list as list_handler
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from handlers import add, list as list_handler
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

    # Обработчик для добавления рекомендаций
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

    # Обработчик для списка рекомендаций
    list_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("list", list_handler.cmd_list)],
        states={
            list_handler.CATEGORY: [MessageHandler(filters.TEXT, list_handler.enter_category)],
            list_handler.SORTING: [MessageHandler(filters.TEXT, list_handler.enter_sorting)],
            list_handler.PAGINATION: [MessageHandler(filters.TEXT, list_handler.navigate)],
        },
        fallbacks=[]
    )

    application.add_handler(list_conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
