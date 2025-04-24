import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.keyboards.message_options import show_message_options

logger = logging.getLogger(__name__)


async def director_announcement(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обработчик кнопки «Сделать объявление…» для дирекции:
    отвечаем на callback и показываем меню выбора получателей.
    """
    query = update.callback_query
    await query.answer()  # асинхронно отвечаем на callback_query
    # далее показываем уже готовую логику выбора получателей
    return await show_message_options(update, context)


async def staff_write_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обработчик кнопки «Написать сообщение…» для сотрудников:
    отвечаем на callback и показываем меню выбора получателей.
    """
    query = update.callback_query
    await query.answer()
    return await show_message_options(update, context)
