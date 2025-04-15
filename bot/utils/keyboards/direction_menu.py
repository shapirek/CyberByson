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

from bot.config import CHOOSE_DIRECTION


async def show_directions_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("НТН", callback_data='НТН')],
        [InlineKeyboardButton("НЕН", callback_data='НЕН')],
        [InlineKeyboardButton("НОН", callback_data='НОН')],
        [InlineKeyboardButton("НФН", callback_data='НФН')],
        [InlineKeyboardButton("Назад", callback_data='back_to_director')]  # Кнопка "Назад"
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Выберите направление:", reply_markup=reply_markup)
    return CHOOSE_DIRECTION
