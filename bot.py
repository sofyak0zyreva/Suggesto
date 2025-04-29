import os
from telegram import BotCommand, Update
from telegram.ext import (
    Application, CommandHandler, ConversationHandler,
    CallbackQueryHandler, CallbackContext, MessageHandler, filters
)
from handlers import add, list, rate, random, help
from dotenv import load_dotenv

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

async def set_bot_commands(app):
    commands = [
        BotCommand("add", "Добавить рекомендацию"),
        BotCommand("rate", "Оценить что-то"),
        BotCommand("random", "Случайная рекомендация"),
        BotCommand("list", "Список рекомендаций"),
        BotCommand("help", "Показать помощь"),
    ]
    await app.bot.set_my_commands(commands)


def main():
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    print(TOKEN)
    application = Application.builder().token(
        TOKEN).post_init(set_bot_commands).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help.cmd_help))

    application.add_handler(ConversationHandler(
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
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('list', list.cmd_list)],
        states={
            list.CATEGORY: [CallbackQueryHandler(list.enter_category)],
            list.SORTING: [CallbackQueryHandler(list.enter_sorting)],
            list.PAGINATION: [CallbackQueryHandler(list.navigate)],
        },
        fallbacks=[]
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('rate', rate.cmd_rate)],
        states={
            rate.CATEGORY: [CallbackQueryHandler(rate.enter_category)],
            rate.RECOMMENDATION: [CallbackQueryHandler(rate.enter_recommendation)],
            rate.RATING: [CallbackQueryHandler(rate.enter_rating)],
        },
        fallbacks=[]
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('random', random.cmd_random)],
        states={
            random.CATEGORY: [
                CallbackQueryHandler(
                    random.show_random, pattern="^(Книга|Фильм|Место|Музыка|another)$"),
                CallbackQueryHandler(random.cancel_random, pattern="^close$")
            ],
        },
        fallbacks=[]
    ))

    application.run_polling()


if __name__ == '__main__':
    main()
