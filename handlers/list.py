# list.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database import Session, Recommendation

# Состояния
CATEGORY, SORTING, PAGINATION = range(3)

CATEGORY_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("📚 Книга", callback_data="Книга"),
     InlineKeyboardButton("🎬 Фильм", callback_data="Фильм")],
    [InlineKeyboardButton("📍 Место", callback_data="Место"), InlineKeyboardButton(
        "🎵 Музыка", callback_data="Музыка")]
])

SORTING_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔥 По рейтингу", callback_data="rating"),
     InlineKeyboardButton("🕰 По дате", callback_data="date")]
])

NAVIGATION_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("◀️ Назад", callback_data="prev"), InlineKeyboardButton(
        "▶️ Вперед", callback_data="next")],
    [InlineKeyboardButton("🎲 Случайная", callback_data="random")],
    [InlineKeyboardButton("❌ Закрыть", callback_data="close")]
])


async def cmd_list(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    context.user_data['page'] = 0
    await update.message.reply_text(
        "Выберите категорию:",
        reply_markup=CATEGORY_KEYBOARD
    )
    return CATEGORY


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

    await query.edit_message_text(
        "Выберите способ сортировки:",
        reply_markup=SORTING_KEYBOARD
    )
    return SORTING


async def enter_sorting(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    sorting = query.data

    category = context.user_data['category']

    session = Session()
    query_db = session.query(Recommendation).filter_by(category=category)
    if sorting == "rating":
        query_db = query_db.order_by(Recommendation.rating.desc())
    else:
        query_db = query_db.order_by(Recommendation.id.desc())
    recommendations = query_db.all()
    session.close()

    context.user_data['recommendations'] = recommendations
    context.user_data['page'] = 0

    await show_page(query, context)

    return PAGINATION


async def show_page(query_or_update, context: CallbackContext) -> None:
    if hasattr(query_or_update, 'callback_query'):
        query = query_or_update.callback_query
    else:
        query = query_or_update

    page = context.user_data['page']
    recommendations = context.user_data['recommendations']
    start = page * 5
    end = start + 5
    page_recommendations = recommendations[start:end]

    if not page_recommendations:
        await query.edit_message_text("Нет рекомендаций для отображения.")
        return

    messages = []
    for rec in page_recommendations:
        parts = [f"{rec.title} — ⭐️ {rec.rating}/5"]
        if rec.author:
            parts.append(f"✍️ {rec.author}")
        if rec.comment:
            parts.append(f"💬 {rec.comment}")
        messages.append("\n".join(parts))

    await query.edit_message_text(
        "\n\n".join(messages),
        reply_markup=NAVIGATION_KEYBOARD
    )


async def navigate(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    text = query.data

    page = context.user_data['page']
    recommendations = context.user_data['recommendations']

    if text == "prev":
        if page > 0:
            context.user_data['page'] = page - 1
            await show_page(query, context)
        else:
            await query.answer("Вы на первой странице.", show_alert=True)

    elif text == "next":
        if (page + 1) * 5 < len(recommendations):
            context.user_data['page'] = page + 1
            await show_page(query, context)
        else:
            await query.answer("Вы на последней странице.", show_alert=True)

    elif text == "random":
        import random
        rec = random.choice(recommendations)
        await query.edit_message_text(
            f"🎲 Случайная рекомендация:\n\n"
            f"{rec.title} — ⭐️ {rec.rating}/5\n"
            f"✍️ {rec.author if rec.author else 'Нет автора'}\n"
            f"💬 {rec.comment if rec.comment else 'Нет комментария'}",
            reply_markup=NAVIGATION_KEYBOARD
        )

    elif text == "close":
        await query.edit_message_text("Вы завершили просмотр.")
        return ConversationHandler.END

    return PAGINATION
