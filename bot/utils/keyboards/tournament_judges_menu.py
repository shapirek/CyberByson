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

from bot.config import CHOOSE_TOURNAMENT


async def show_tournament_judges_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    # Список турниров
    tournaments = ["ФМТ", "ГУТ", "БХТ"]

    # Создаем кнопки для каждого турнира
    keyboard = [
        [InlineKeyboardButton(tournament, callback_data=f'tournament_{tournament}')] for tournament in tournaments
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_message_options')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Выберите турнир:", reply_markup=reply_markup)
    return CHOOSE_TOURNAMENT
