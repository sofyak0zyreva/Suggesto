from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from database import Session, Recommendation

# Состояния
CATEGORY, SORTING = range(2)

# Клавиатуры
CATEGORY_KEYBOARD = ReplyKeyboardMarkup([
    ["📚 Книга", "🎬 Фильм"],
    ["📍 Место", "🎵 Музыка"]
], resize_keyboard=True, one_time_keyboard=True)

SORTING_KEYBOARD = ReplyKeyboardMarkup([
    ["🔥 По рейтингу", "🕰 По дате"]
], resize_keyboard=True, one_time_keyboard=True)

# Маппинг эмодзи-категорий на чистые значения
CATEGORY_MAP = {
    "📚 Книга": "Книга",
    "🎬 Фильм": "Фильм",
    "📍 Место": "Место",
    "🎵 Музыка": "Музыка"
}


async def cmd_list(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Выберите категорию:",
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
        "Выберите способ сортировки:",
        reply_markup=SORTING_KEYBOARD
    )
    return SORTING


async def enter_sorting(update: Update, context: CallbackContext) -> int:
    sorting = update.message.text
    if sorting not in ["🔥 По рейтингу", "🕰 По дате"]:
        await update.message.reply_text(
            "Пожалуйста, выберите способ сортировки с помощью кнопок.",
            reply_markup=SORTING_KEYBOARD
        )
        return SORTING

    category = context.user_data['category']
    session = Session()

    query = session.query(Recommendation).filter_by(category=category)

    # Сортировка
    if sorting == "🔥 По рейтингу":
        query = query.order_by(Recommendation.rating.desc())
    elif sorting == "🕰 По дате":
        query = query.order_by(Recommendation.id.desc())

    recommendations = query.limit(5).all()
    session.close()

    if not recommendations:
        await update.message.reply_text(
            "Пока нет рекомендаций в этой категории.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    # Собираем текст для вывода
    messages = []
    for rec in recommendations:
        parts = [f"{rec.title} — ⭐️ {rec.rating}/5"]

        if category == "Место":
            if rec.author:
                parts.append(f"📍 {rec.author}")
            if rec.comment:
                parts.append(f"💬 {rec.comment}")
        elif category == "Фильм":
            if rec.comment:
                parts.append(f"💬 {rec.comment}")
        else:  # Книга или Музыка
            if rec.author:
                parts.append(f"✍️ {rec.author}")
            if rec.comment:
                parts.append(f"💬 {rec.comment}")

        messages.append("\n".join(parts))

    # Отправляем всё одним сообщением
    await update.message.reply_text(
        "\n\n".join(messages),
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
