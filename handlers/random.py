from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import Session, Recommendation, User
import random

# Состояния
CATEGORY = 0

# Клавиатура выбора категории
CATEGORY_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("📚 Книга", callback_data="Книга"),
     InlineKeyboardButton("🎬 Фильм", callback_data="Фильм")],
    [InlineKeyboardButton("📍 Место", callback_data="Место"),
     InlineKeyboardButton("🎵 Музыка", callback_data="Музыка")]
])

# Клавиатура после показа рекомендации
AFTER_RANDOM_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎲 Ещё одну!", callback_data="another")],
    [InlineKeyboardButton("❌ Закрыть", callback_data="close")]
])

# /random


async def cmd_random(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Выберите категорию:",
        reply_markup=CATEGORY_KEYBOARD
    )
    return CATEGORY

# Обработка выбора категории или запроса "ещё одну"


# Обработка выбора категории или запроса "ещё одну"
async def show_random(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

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


    # Обработка первой категории или запроса ещё одной
    if query.data != "another":
        context.user_data['category'] = query.data

    category = context.user_data['category']

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

    rec = random.choice(recommendations)

    # Формируем сообщение динамически
    message_lines = [
        f"🎲 Твой случайный выбор:",
        f"🏆 {rec.title} – ⭐ {rec.rating:.1f}/5"
    ]

    if rec.author:
        message_lines.append(f"⚡️ {rec.author}")
    if rec.comment:
        message_lines.append(f"📝 Комментарий: {rec.comment}")

    message_text = "\n".join(message_lines)

    await query.edit_message_text(
        message_text,
        reply_markup=AFTER_RANDOM_KEYBOARD
    )

    return CATEGORY

# Обработка кнопки "Закрыть"


async def cancel_random(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Закрыто.")
    return ConversationHandler.END
