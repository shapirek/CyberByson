from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from bot.config import STAFF_ACTION


async def show_staff_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Проверяем, есть ли сообщение в update
    chat_id = update.effective_chat.id

    keyboard = [
        [InlineKeyboardButton("НОВОСТИ", callback_data='news')],
        [InlineKeyboardButton("Запросить технику", callback_data='request_equipment')],
        [InlineKeyboardButton("Выдать наряд", callback_data='assign_duty')],
        [InlineKeyboardButton("Написать сообщение...", callback_data='staff_write_message')],
        [InlineKeyboardButton("Написать слона/педаль", callback_data='staff_write_something')],
        [InlineKeyboardButton("Турниры", callback_data='staff_tournaments')],
        [InlineKeyboardButton("Дежурство", callback_data='nadzor')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text="Меню сотрудников:", reply_markup=reply_markup)
    return STAFF_ACTION
