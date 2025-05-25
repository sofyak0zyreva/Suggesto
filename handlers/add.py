# add.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from database import Session, Recommendation, User, Rating

# Состояния
CATEGORY, TITLE, AUTHOR, COMMENT, RATING = range(5)

# Клавиатуры
CATEGORY_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("📚 Книга", callback_data="Книга"),
     InlineKeyboardButton("🎬 Фильм", callback_data="Фильм")],
    [InlineKeyboardButton("📍 Место", callback_data="Место"), InlineKeyboardButton(
        "🎵 Музыка", callback_data="Музыка")]
])

RATING_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("⭐️", callback_data="1"),
     InlineKeyboardButton("⭐️⭐️", callback_data="2")],
    [InlineKeyboardButton("⭐️⭐️⭐️", callback_data="3"),
     InlineKeyboardButton("⭐️⭐️⭐️⭐️", callback_data="4")],
    [InlineKeyboardButton("⭐️⭐️⭐️⭐️⭐️", callback_data="5")]
])

SKIP_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("Пропустить", callback_data="skip")]
])

# Команда для добавления рекомендации


async def cmd_add(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Выберите категорию для вашей рекомендации:",
        reply_markup=CATEGORY_KEYBOARD
    )
    return CATEGORY

# Выбор категории


async def enter_category(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    category = query.data

    context.user_data['category'] = category
    await query.edit_message_text(
        "Введите название рекомендации:"
    )
    return TITLE

# Ввод названия


async def enter_title(update: Update, context: CallbackContext) -> int:
    title = update.message.text
    context.user_data['title'] = title

    category = context.user_data['category']

    if category == "Фильм":
        context.user_data['author'] = None
        await update.message.reply_text(
            "Введите комментарий (по желанию):",
            reply_markup=SKIP_KEYBOARD
        )
        return COMMENT
    else:
        prompt = "Введите автора (по желанию):" if category in [
            "Книга", "Музыка"] else "Введите адрес (по желанию):"
        await update.message.reply_text(
            prompt,
            reply_markup=SKIP_KEYBOARD
        )
        return AUTHOR

# Ввод автора/адреса


async def enter_author(update: Update, context: CallbackContext) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        context.user_data['author'] = None
        await query.edit_message_text(
            "Введите комментарий (по желанию):",
            reply_markup=SKIP_KEYBOARD
        )
    else:
        author = update.message.text
        context.user_data['author'] = author
        await update.message.reply_text(
            "Введите комментарий (по желанию):",
            reply_markup=SKIP_KEYBOARD
        )
    return COMMENT

# Ввод комментария


async def enter_comment(update: Update, context: CallbackContext) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        context.user_data['comment'] = None
        await query.edit_message_text(
            "Выберите оценку:",
            reply_markup=RATING_KEYBOARD
        )
    else:
        comment = update.message.text
        context.user_data['comment'] = comment
        await update.message.reply_text(
            "Выберите оценку:",
            reply_markup=RATING_KEYBOARD
        )
    return RATING

# Выбор рейтинга


async def enter_rating(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    rating = int(query.data)

    category = context.user_data['category']
    title = context.user_data['title']
    author = context.user_data['author']
    comment = context.user_data['comment']

    user_id = query.from_user.id
    print(f"user_id in add: enter_rating", user_id)
    username = query.from_user.username

    chat_id = update.effective_chat.id
    print(f"chat_id in add: enter_rating", chat_id)
    chat = update.effective_chat
    print(f"chat type in add: enter_rating", chat.type)
    session = Session()

    user = session.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        user = User(telegram_id=user_id, username=username)
        session.add(user)
        session.commit()

    recommendation = Recommendation(
        category=category,
        title=title,
        author=author,
        comment=comment,
        rating=rating,
        user_id=user.id,
        chat_id=chat_id
    )
    session.add(recommendation)
    session.commit()

    initial_rating = Rating(
        user_id=user.id,
        recommendation_id=recommendation.id,
        rating=rating
    )
    session.add(initial_rating)

    session.commit()
    session.close()

    await query.edit_message_text(
        f"✅ Ваша рекомендация добавлена!\n\n"
        f"Категория: {category}\n"
        f"Название: {title}\n"
        f"Автор: {author if author else 'Не указан'}\n"
        f"Комментарий: {comment if comment else 'Не указан'}\n"
        f"Оценка: {rating}/5"
    )
    context.user_data.clear()
    return ConversationHandler.END
