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


async def show_main_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ['Школьники', 'Сотрудники'],
        ['Родители'],
        ['Завершить диалог']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)
