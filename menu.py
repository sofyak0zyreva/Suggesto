from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

# Создаем главную клавиатуру с кнопкой "Меню"
MENU_KEYBOARD = ReplyKeyboardMarkup([
    [KeyboardButton("≡ Меню")]  # Кнопка меню
], resize_keyboard=True)

# Создаем клавиатуру с подсказками команд, которая будет показываться при нажатии на "Меню"
COMMANDS_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("Добавить рекомендацию", callback_data='/add')],
    [InlineKeyboardButton("Оценить что-то", callback_data='/rate')],
    [InlineKeyboardButton("Случайная рекомендация", callback_data='/random')],
    [InlineKeyboardButton("Список рекомендаций", callback_data='/list')],
    [InlineKeyboardButton("Помощь с командами.", callback_data='/help')],
    [InlineKeyboardButton("Закрыть", callback_data='close_menu')]
])

# Обработчик команды /start


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Привет! Я бот, который поможет тебе с рекомендациями. Для доступа к меню, нажми кнопку ниже.",
        reply_markup=MENU_KEYBOARD  # Отправляем клавиатуру с кнопкой "Меню"
    )

# Обработчик кнопки "Меню"


async def show_menu(update: Update, context: CallbackContext) -> None:
    # Появляется меню с подсказками команд
    await update.message.reply_text(
        "Вот что я умею:",
        reply_markup=COMMANDS_KEYBOARD  # Отправляем меню с командами
    )

# Обработчик нажатия на команду меню


async def handle_menu_commands(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'close_menu':
        await query.edit_message_text("Меню закрыто.")  # Закрытие меню
    elif query.data == '/add':
        await query.edit_message_text("Добавить рекомендацию.")
        # Здесь можно продолжить работу с командой /add
    elif query.data == '/rate':
        await query.edit_message_text("Оценить что-то.")
        # Здесь можно продолжить работу с командой /rate
    elif query.data == '/random':
        await query.edit_message_text("Случайная рекомендация.")
        # Здесь можно продолжить работу с командой /random
    elif query.data == '/list':
        await query.edit_message_text("Список рекомендаций.")
        # Здесь можно продолжить работу с командой /list
    elif query.data == '/help':
        await query.edit_message_text("Помощь с командами.")
