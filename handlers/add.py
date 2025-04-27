# handlers/add.py
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from database import Session, Recommendation, User

# Состояния
CATEGORY, TITLE, AUTHOR, COMMENT, RATING = range(5)

# Клавиатуры
CATEGORY_KEYBOARD = ReplyKeyboardMarkup([
    ["📚 Книга", "🎬 Фильм"],
    ["📍 Место", "🎵 Музыка"]
], resize_keyboard=True, one_time_keyboard=True)

SKIP_KEYBOARD = ReplyKeyboardMarkup([
    [KeyboardButton("Пропустить")]
], resize_keyboard=True, one_time_keyboard=True)

RATING_KEYBOARD = ReplyKeyboardMarkup([
    ["⭐️", "⭐️⭐️"],
    ["⭐️⭐️⭐️", "⭐️⭐️⭐️⭐️"],
    ["⭐️⭐️⭐️⭐️⭐️"]
], resize_keyboard=True, one_time_keyboard=True)

# Маппинг эмодзи-категорий на чистые значения
CATEGORY_MAP = {
    "📚 Книга": "Книга",
    "🎬 Фильм": "Фильм",
    "📍 Место": "Место",
    "🎵 Музыка": "Музыка"
}

# Маппинг звездочек на оценку
STAR_TO_RATING = {
    "⭐️": 1,
    "⭐️⭐️": 2,
    "⭐️⭐️⭐️": 3,
    "⭐️⭐️⭐️⭐️": 4,
    "⭐️⭐️⭐️⭐️⭐️": 5
}


async def cmd_add(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Выберите категорию для вашей рекомендации:",
        reply_markup=CATEGORY_KEYBOARD
    )
    return CATEGORY


async def enter_category(update: Update, context: CallbackContext) -> int:
    category_emoji = update.message.text
    if category_emoji not in CATEGORY_MAP:
        await update.message.reply_text(
            "Пожалуйста, выберите категорию с помощью кнопок.",
            reply_markup=CATEGORY_KEYBOARD
        )
        return CATEGORY

    context.user_data['category'] = CATEGORY_MAP[category_emoji]
    await update.message.reply_text(
        "Введите название рекомендации:",
        reply_markup=ReplyKeyboardRemove()
    )
    return TITLE


async def enter_title(update: Update, context: CallbackContext) -> int:
    title = update.message.text
    context.user_data['title'] = title

    await update.message.reply_text(
        "Введите автора или адрес (по желанию):",
        reply_markup=SKIP_KEYBOARD
    )
    return AUTHOR


async def enter_author(update: Update, context: CallbackContext) -> int:
    author = update.message.text
    context.user_data['author'] = None if author == "Пропустить" else author

    await update.message.reply_text(
        "Введите комментарий (по желанию):",
        reply_markup=SKIP_KEYBOARD
    )
    return COMMENT


async def enter_comment(update: Update, context: CallbackContext) -> int:
    comment = update.message.text
    context.user_data['comment'] = None if comment == "Пропустить" else comment

    await update.message.reply_text(
        "Выберите оценку:",
        reply_markup=RATING_KEYBOARD
    )
    return RATING


async def enter_rating(update: Update, context: CallbackContext) -> int:
    stars = update.message.text
    rating = STAR_TO_RATING.get(stars)

    if not rating:
        await update.message.reply_text(
            "Пожалуйста, выберите оценку с помощью кнопок.",
            reply_markup=RATING_KEYBOARD
        )
        return RATING

    category = context.user_data['category']
    title = context.user_data['title']
    author = context.user_data['author']
    comment = context.user_data['comment']

    user_id = update.message.from_user.id
    username = update.message.from_user.username

    session = Session()

    # Проверяем наличие пользователя
    user = session.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        user = User(telegram_id=user_id, username=username)
        session.add(user)
        session.commit()

    # Сохраняем рекомендацию
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
    session.close()

    await update.message.reply_text(
        f"✅ Ваша рекомендация добавлена!\n\n"
        f"Категория: {category}\n"
        f"Название: {title}\n"
        f"Автор: {author if author else 'Не указан'}\n"
        f"Комментарий: {comment if comment else 'Не указан'}\n"
        f"Оценка: {rating}/5",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
