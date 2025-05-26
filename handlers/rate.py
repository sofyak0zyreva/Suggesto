from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import Session, Recommendation, Rating, User

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

# Команда для начала оценки


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

    user_id = query.from_user.id
    username = query.from_user.username

    session = Session()

    user = session.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        user = User(telegram_id=user_id, username=username)
        session.add(user)
        session.commit()

    user_id = user.id
    print(f"user_id in rate: enter_category", user_id)

    context.user_data['category'] = category
    context.user_data['page'] = 0

    session = Session()
    chat = update.effective_chat
    if chat.type == "private":
        # личный чат: только свои рекомендации
        recommendations = session.query(Recommendation).filter_by(
            category=category,
            user_id=user_id
        ).all()
    else:
        # групповой чат: все рекомендации чата
        recommendations = session.query(Recommendation).filter_by(
            category=category,
            chat_id=chat.id
        ).all()
    # recommendations = session.query(
    #     Recommendation).filter_by(category=category, user_id=user_id).all()
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

    # Сохраняем ID выбранной рекомендации
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
    username = query.from_user.username

    session = Session()

    user = session.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        user = User(telegram_id=user_id, username=username)
        session.add(user)
        session.commit()
    user_id = user.id
    print(f"user_id in rate: enter_recommendation", user_id)

    session = Session()
    existing_rating = session.query(Rating).filter_by(
        recommendation_id=recommendation_id, user_id=user_id).first()
    session.close()

    if existing_rating:
        await query.edit_message_text(f"Вы уже оценили эту рекомендацию. Ваш рейтинг: {existing_rating.rating}⭐")
        return ConversationHandler.END

    # Сохраняем рекомендацию в context для использования в следующем шаге
    context.user_data['recommendation'] = recommendation

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

    recommendation = context.user_data.get('recommendation')

    if recommendation is None:
        await query.edit_message_text("Ошибка: Рекомендация не найдена.")
        context.user_data.clear()
        return ConversationHandler.END

    user_id = query.from_user.id
    username = query.from_user.username
    recommendation_id = recommendation.id

    # Проверяем, чтобы рейтинг был корректным
    if rating < 1 or rating > 5:
        await query.edit_message_text("Ошибка: рейтинг должен быть от 1 до 5.")
        context.user_data.clear()
        return ConversationHandler.END

    # Создаем новый рейтинг и сохраняем его в базе данных
    session = Session()
    user = session.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        user = User(telegram_id=user_id, username=username)
        session.add(user)
        session.commit()
    user_id = user.id
    print(f"user_id in rate: enter_rating", user_id)
    new_rating = Rating(
        user_id=user_id, recommendation_id=recommendation_id, rating=rating)
    session.add(new_rating)

    # Пересчитываем средний рейтинг для рекомендации
    all_ratings = session.query(Rating).filter_by(
        recommendation_id=recommendation_id).all()
    total_rating = sum(rating.rating for rating in all_ratings)
    recommendation.average_rating = total_rating / len(all_ratings)
    recommendation.rating_count = len(all_ratings)

    session.commit()
    session.close()

    # Отправляем сообщение с подтверждением
    await query.edit_message_text(
        f"✅ Ваш рейтинг: {rating}⭐\n"
        f"Средний рейтинг: {recommendation.average_rating:.2f}/5 "
    )

    # Очищаем user_data после завершения
    context.user_data.clear()

    return ConversationHandler.END
