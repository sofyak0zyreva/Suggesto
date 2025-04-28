from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import Session, Recommendation, Rating

# Состояния
CATEGORY, RECOMMENDATION, RATING = range(3)

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

# Команда для оценки


async def cmd_rate(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Выберите категорию для оценки:",
        reply_markup=CATEGORY_KEYBOARD
    )
    return CATEGORY

# Выбор категории


async def enter_category(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    category = query.data

    context.user_data['category'] = category
    context.user_data['page'] = 0

    session = Session()
    recommendations = session.query(
        Recommendation).filter_by(category=category).all()
    session.close()

    if not recommendations:
        await query.edit_message_text("Пока нет рекомендаций в этой категории.")
        return ConversationHandler.END

    context.user_data['recommendations'] = recommendations

    # Отправляем пользователю рекомендации
    keyboard = [
        [InlineKeyboardButton(
            rec.title, callback_data=f"recommendation:{rec.id}")]
        for rec in recommendations
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "Выберите рекомендацию для оценки:",
        reply_markup=markup
    )
    return RECOMMENDATION

# Выбор рекомендации


async def enter_recommendation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    recommendation_id = int(query.data.split(":")[1])

    context.user_data['recommendation_id'] = recommendation_id

    # Получаем выбранную рекомендацию из базы данных
    session = Session()
    recommendation = session.query(Recommendation).filter_by(
        id=recommendation_id).first()
    session.close()

    if not recommendation:
        await query.edit_message_text("Рекомендация не найдена.")
        return ConversationHandler.END

    # Проверяем, ставил ли пользователь уже рейтинг
    user_id = query.from_user.id
    session = Session()
    existing_rating = session.query(Rating).filter_by(
        recommendation_id=recommendation_id, user_id=user_id).first()
    session.close()

    if existing_rating:
        await query.edit_message_text(f"Вы уже оценили эту рекомендацию. Ваш рейтинг: {existing_rating.rating}⭐")
        return ConversationHandler.END

    # Отправляем пользователю клавиатуру для выбора рейтинга
    await query.edit_message_text(
        "Выберите оценку для этой рекомендации:",
        reply_markup=RATING_KEYBOARD
    )
    return RATING

# Выбор рейтинга


async def enter_rating(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    rating = int(query.data)

    recommendation_id = context.user_data['recommendation_id']
    user_id = query.from_user.id

    # Получаем объект recommendation из context (предположим, что он был загружен заранее)
    recommendation = context.user_data.get('recommendation')

    if recommendation is None:
        await query.edit_message_text("Ошибка: Рекомендация не найдена.")
        context.user_data.clear()
        return ConversationHandler.END

    # Проверяем, чтобы рейтинг был корректным
    if rating < 1 or rating > 5:
        await query.edit_message_text("Ошибка: рейтинг должен быть от 1 до 5.")
        context.user_data.clear()
        return ConversationHandler.END

    # Создаем новый рейтинг (предположим, что у нас есть способ добавить его в список)
    new_rating = {'user_id': user_id, 'rating': rating}

    # Добавляем новый рейтинг в рекомендации
    if 'ratings' not in recommendation:
        recommendation['ratings'] = []

    recommendation['ratings'].append(new_rating)

    # Пересчитываем средний рейтинг
    total_rating = sum(r['rating'] for r in recommendation['ratings'])
    rating_count = len(recommendation['ratings'])
    recommendation['average_rating'] = total_rating / rating_count
    recommendation['rating_count'] = rating_count

    # Отправляем сообщение с обновленным рейтингом
    await query.edit_message_text(
        f"✅ Ваш рейтинг: {rating}⭐\n"
        f"Средний рейтинг: {recommendation['average_rating']:.2f}/5 ({recommendation['rating_count']} оценок)"
    )

    # Очищаем user_data после завершения
    context.user_data.clear()

    return ConversationHandler.END
