# handlers/add.py
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from database import Session, Recommendation, User


async def cmd_add(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Введите категорию для вашей рекомендации (например, книги, фильмы, рестораны):"
    )
    return "CATEGORY"


async def enter_category(update: Update, context: CallbackContext) -> None:
    category = update.message.text
    context.user_data['category'] = category

    # Запрашиваем название рекомендации
    await update.message.reply_text("Введите название рекомендации:")
    return "TITLE"


async def enter_title(update: Update, context: CallbackContext) -> None:
    title = update.message.text
    context.user_data['title'] = title

    # Запрашиваем автора (опционально)
    await update.message.reply_text("Введите автора (необязательно):")
    return "AUTHOR"


async def enter_author(update: Update, context: CallbackContext) -> None:
    author = update.message.text
    context.user_data['author'] = author if author else None

    # Запрашиваем комментарий
    await update.message.reply_text("Введите комментарий (необязательно):")
    return "COMMENT"


async def enter_comment(update: Update, context: CallbackContext) -> None:
    comment = update.message.text
    context.user_data['comment'] = comment if comment else None

    # Запрашиваем оценку
    await update.message.reply_text("Введите оценку от 1 до 5:")
    return "RATING"


async def enter_rating(update: Update, context: CallbackContext) -> None:
    rating = update.message.text
    if rating.isdigit() and 1 <= int(rating) <= 5:
        rating = int(rating)
        category = context.user_data['category']
        title = context.user_data['title']
        author = context.user_data['author']
        comment = context.user_data['comment']

        # Получаем информацию о пользователе
        user_id = update.message.from_user.id
        session = Session()

        # Проверим, есть ли пользователь в базе данных
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            # Если пользователя нет, добавляем нового
            user = User(telegram_id=user_id,
                        username=update.message.from_user.username)
            session.add(user)
            session.commit()

        # Сохранение рекомендации
        recommendation = Recommendation(
            category=category,
            title=title,
            author=author,
            comment=comment,
            rating=rating,
            user_id=user.id
        )
        session.add(recommendation)
        session.commit()

        # Отправка сообщения о добавлении рекомендации
        await update.message.reply_text(f"✅ Ваша рекомендация добавлена!\n\n"
                                        f"Категория: {category}\n"
                                        f"Название: {title}\n"
                                        f"Автор: {author if author else 'Не указан'}\n"
                                        f"Комментарий: {comment if comment else 'Не указан'}\n"
                                        f"Оценка: {rating}/5")

        # Завершаем процесс добавления
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, введите оценку от 1 до 5.")
        return "RATING"
