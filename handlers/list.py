from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from database import Session, Recommendation

# Состояния
CATEGORY, SORTING, PAGINATION = range(3)

# Клавиатуры
CATEGORY_KEYBOARD = ReplyKeyboardMarkup([
    ["📚 Книга", "🎬 Фильм"],
    ["📍 Место", "🎵 Музыка"]
], resize_keyboard=True, one_time_keyboard=True)

SORTING_KEYBOARD = ReplyKeyboardMarkup([
    ["🔥 По рейтингу", "🕰 По дате"]
], resize_keyboard=True, one_time_keyboard=True)

NAVIGATION_KEYBOARD = ReplyKeyboardMarkup([
    ["◀️ Назад", "▶️ Вперед"],
    ["🎲 Случайная", "❌ Закрыть"]
], resize_keyboard=True, one_time_keyboard=True)

# Маппинг эмодзи-категорий на чистые значения
CATEGORY_MAP = {
    "📚 Книга": "Книга",
    "🎬 Фильм": "Фильм",
    "📍 Место": "Место",
    "🎵 Музыка": "Музыка"
}


async def cmd_list(update: Update, context: CallbackContext) -> int:
    print("cmd_list: Очистка данных пользователя и инициализация.")
    context.user_data.clear()  # Очищаем старые данные пользователя перед новым процессом

    # Инициализация данных для пагинации
    context.user_data['page'] = 0  # Убедитесь, что 'page' всегда есть
    print("cmd_list: Инициализирована страница с нулевым значением.")

    await update.message.reply_text(
        "Выберите категорию:",
        reply_markup=CATEGORY_KEYBOARD
    )
    return CATEGORY


async def enter_category(update: Update, context: CallbackContext) -> int:
    category_emoji = update.message.text
    print(f"enter_category: Выбрана категория: {category_emoji}")

    if category_emoji not in CATEGORY_MAP:
        await update.message.reply_text(
            "Пожалуйста, выберите категорию с помощью кнопок.",
            reply_markup=CATEGORY_KEYBOARD
        )
        return CATEGORY

    context.user_data['category'] = CATEGORY_MAP[category_emoji]
    print(
        f"enter_category: Установлена категория: {context.user_data['category']}")

    # Инициализируем пагинацию и рекомендации
    context.user_data['page'] = 0
    context.user_data['recommendations'] = []

    # Проверяем, есть ли рекомендации в выбранной категории
    category = context.user_data['category']
    session = Session()
    recommendations = session.query(
        Recommendation).filter_by(category=category).all()
    session.close()

    if not recommendations:
        await update.message.reply_text(
            "Пока нет рекомендаций в этой категории.",
            reply_markup=ReplyKeyboardRemove()
        )
        print("enter_category: Нет рекомендаций в выбранной категории.")
        return ConversationHandler.END

    # Сохраняем рекомендации для пагинации
    context.user_data['recommendations'] = recommendations
    print(f"enter_category: Загружено {len(recommendations)} рекомендаций.")

    # Показываем сортировку
    await update.message.reply_text(
        "Выберите способ сортировки:",
        reply_markup=SORTING_KEYBOARD
    )
    return SORTING


async def enter_sorting(update: Update, context: CallbackContext) -> int:
    sorting = update.message.text
    print(f"enter_sorting: Выбран способ сортировки: {sorting}")

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

    recommendations = query.all()
    session.close()

    # Сохраняем рекомендации для пагинации
    context.user_data['recommendations'] = recommendations
    context.user_data['page'] = 0  # Начинаем с первой страницы

    print(
        f"enter_sorting: Загружено {len(recommendations)} рекомендаций после сортировки.")

    # Показываем первые 5 рекомендаций
    await show_page(update, context)

    return PAGINATION


async def show_page(update: Update, context: CallbackContext) -> None:
    # Получаем текущую страницу и рекомендации
    page = context.user_data['page']
    recommendations = context.user_data['recommendations']

    # Определяем отступ для вывода
    start = page * 5
    end = start + 5
    page_recommendations = recommendations[start:end]

    print(
        f"show_page: Отображение страницы {page}. Показываем с {start} по {end} рекомендацию.")

    # Собираем текст для вывода
    category = context.user_data['category']
    messages = []
    for rec in page_recommendations:
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

    # Отправляем список рекомендаций
    if len(recommendations) > 5:
        # Если рекомендаций больше 5, показываем кнопки навигации
        await update.message.reply_text(
            "\n\n".join(messages),
            reply_markup=NAVIGATION_KEYBOARD
        )
    else:
        # Если рекомендаций 5 или меньше, не показываем кнопки навигации
        await update.message.reply_text(
            "\n\n".join(messages),
            reply_markup=ReplyKeyboardRemove()
        )


async def navigate(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    

 # Если пользователь отправил команду /list, начинаем заново
    if text == "/list":
        context.user_data.clear()
        await cmd_list(update, context)
        return CATEGORY
    print(f"navigate: Выбрана опция: {text}")
    # Получаем текущую страницу, если она есть
    # По умолчанию страница 0, если нет данных
    page = context.user_data.get('page', 0)
    recommendations = context.user_data.get('recommendations', [])
    total_recommendations = len(recommendations)

    print(
        f"navigate: Текущая страница: {page}, всего рекомендаций: {total_recommendations}")

    # Если нажали "◀️ Назад"
    if text == "◀️ Назад":
        if page > 0:  # Если не на первой странице, идем назад
            context.user_data['page'] = page - 1
            await show_page(update, context)
        else:
            # Если на первой странице, ничего не делаем, просто не обновляем страницу
            await update.message.reply_text(
                "Вы на первой странице.",
                reply_markup=NAVIGATION_KEYBOARD
            )

    # Если нажали "▶️ Вперед"
    elif text == "▶️ Вперед":
        if (page + 1) * 5 < total_recommendations:  # Если есть еще страницы вперед
            context.user_data['page'] = page + 1
            await show_page(update, context)
        else:
            # Если нет страниц вперед, ничего не делаем, просто не обновляем страницу
            await update.message.reply_text(
                "Вы на последней странице.",
                reply_markup=NAVIGATION_KEYBOARD
            )

    # Если выбрали случайную рекомендацию
    elif text == "🎲 Случайная":
        import random
        rec = random.choice(recommendations)
        await update.message.reply_text(
            f"🎲 Случайная рекомендация: {rec.title} — ⭐️ {rec.rating}/5\n"
            f"Комментарий: {rec.comment if rec.comment else 'Не указан'}",
            reply_markup=NAVIGATION_KEYBOARD
        )

    # Закрытие просмотра
    elif text == "❌ Закрыть":
        await update.message.reply_text(
            "Вы завершили просмотр.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    return PAGINATION
