from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import PARENTS_ACTION
from bot.services.google_sheets.read_2 import read_google_sheet_sheet2
from .env import TABULA_kids

import logging

logger = logging.getLogger(__name__)


async def show_parents_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        # Загружаем данные из Листа 2 таблицы школьников
        kids_data = await read_google_sheet_sheet2(TABULA_kids)
        context.user_data['kids_data'] = kids_data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных школьников: {e}")
        await update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Пусть ребенок мне позвонит!", callback_data='parent_call')],
        [InlineKeyboardButton("Что привезти ребенку?", callback_data='parent_gift')],
        [InlineKeyboardButton("Расписание КЛШ", callback_data='parent_schedule')],
        [InlineKeyboardButton("Телефоны дирекции", callback_data='parent_director_phones')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите опцию для родителей:", reply_markup=reply_markup)
    return PARENTS_ACTION
