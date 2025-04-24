# bot/handlers/news.py

import logging
import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.google_sheets.read_schedule import read_schedule_sheet
from bot.services.dates import get_current_date, normalize_table_date
from bot.utils.schedule import format_schedule_message
from .env import SCHEDULE_SHEET_URL

logger = logging.getLogger(__name__)


async def handle_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Асинхронно обрабатывает запрос новостей, берёт расписание для текущей даты
    и присылает пользователю либо данные, либо сообщение об отсутствии событий.
    """
    target = update.effective_message

    try:
        # 1) Загрузка расписания один раз и кеширование
        if 'schedule_data' not in context.bot_data:
            # read_schedule_sheet — синхронная, запускаем в background-потоке
            context.bot_data['schedule_data'] = await asyncio.to_thread(
                read_schedule_sheet, SCHEDULE_SHEET_URL
            )

        schedule_data = context.bot_data['schedule_data']

        # 2) Поиск сегодняшнего блока
        today = get_current_date()
        today_schedule = next(
            (item for item in schedule_data
             if 'дата' in item and normalize_table_date(item['дата']) == today),
            None
        )

        # 3) Формирование текста ответа
        if today_schedule:
            response_text = format_schedule_message(today_schedule, schedule_data)
        else:
            response_text = "📭 На сегодня новостей нет!"

        # 4) Отправка ответа
        if update.callback_query:
            await update.callback_query.answer()
            await context.bot.send_message(
                chat_id=target.chat_id,
                text=response_text,
                parse_mode='Markdown'
            )
        else:
            await target.reply_text(response_text, parse_mode='Markdown')

        logger.info(f"handle_news: sent schedule for {today}")

    except Exception as e:
        logger.error(f"Error in handle_news: {e}", exc_info=True)
        err_text = "⚠️ Не удалось загрузить расписание. Попробуйте позже."
        if update.callback_query:
            # show_alert чтобы не спамить чат
            await update.callback_query.answer(err_text, show_alert=True)
        else:
            await target.reply_text(err_text)
