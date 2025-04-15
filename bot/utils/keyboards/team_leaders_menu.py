from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)

from bot.config import CHOOSE_TEAM


async def show_team_leaders_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    # Греческий алфавит
    teams = [
        "Альфа", "Бета", "Гамма", "Дельта", "Эпсилон", "Эта", "Тета",
        "Йота", "Каппа", "Лямбда", "Мю", "Ню", "Кси", "Омикрон", "Пи", "Ро",
        "Сигма", "Тау", "Ипсилон", "Фи", "Хи", "Пси", "Омега"
    ]

    # Создаем кнопки для каждой команды
    keyboard = [
        [InlineKeyboardButton(team, callback_data=f'team_{team}')] for team in teams
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_message_options')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Выберите команду:", reply_markup=reply_markup)
    return CHOOSE_TEAM
