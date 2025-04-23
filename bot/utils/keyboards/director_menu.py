from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from bot.config import DIRECTOR_ACTION


async def show_director_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Проверяем, есть ли сообщение в update
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id

    keyboard = [
        [InlineKeyboardButton("НОВОСТИ", callback_data='news')],
        [InlineKeyboardButton("Сделать объявление...", callback_data='director_announcement')],
        [InlineKeyboardButton("Написать слона/педаль", callback_data='staff_write_something')],
        [InlineKeyboardButton("Попросить купить", callback_data='buy')],
        [InlineKeyboardButton("Узнать контакты", callback_data='director_employee_contacts')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text="Меню дирекции:", reply_markup=reply_markup)
    return DIRECTOR_ACTION
