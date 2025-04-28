from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from handlers import add, list, rate
from config import TOKEN


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Привет! Я бот для рекомендаций.\n" 
        "📚 Фильмы, книги, музыка, места – всё в одном месте!🔹 Как начать?\n"
        "/add – добавить рекомендацию\n"
        "/rate – оценить рекомендацию\n"
        "/list – список рекомендаций\n"
        "/random – случайная рекомендация\n"
        "/help – помощь"
    )


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add.cmd_add)],
        states={
            add.CATEGORY: [CallbackQueryHandler(add.enter_category)],
            add.TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add.enter_title)],
            add.AUTHOR: [
                CallbackQueryHandler(add.enter_author, pattern="^skip$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               add.enter_author)
            ],
            add.COMMENT: [
                CallbackQueryHandler(add.enter_comment, pattern="^skip$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               add.enter_comment)
            ],
            add.RATING: [CallbackQueryHandler(add.enter_rating)],
        },
        fallbacks=[]
    )


    # ConversationHandler для команды /list
    list_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('list', list.cmd_list)],
        states={
            list.CATEGORY: [CallbackQueryHandler(list.enter_category)],
            list.SORTING: [CallbackQueryHandler(list.enter_sorting)],
            list.PAGINATION: [CallbackQueryHandler(list.navigate)],
        },
        fallbacks=[]
    )
    application.add_handler(add_conv_handler)


    application.add_handler(list_conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
