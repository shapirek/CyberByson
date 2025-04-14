from telegram import Update
from telegram.ext import CallbackContext
import logging  # для логирования
from your_date_utils import normalize_table_date, get_current_date  # ваши утилиты для работы с датами
from your_schedule_utils import read_schedule_sheet, format_schedule_message  # ваши функции для работы с расписанием
import asyncio  # для асинхронной версии


async def handle_news(update: Update, context: CallbackContext) -> None:
    """
    Асинхронно обрабатывает запрос новостей с оптимизированной загрузкой данных
    """
    try:
        # Получаем объект сообщения
        query = update.callback_query
        message = query.message if query else update.message
        
        # Асинхронная загрузка данных
        if 'schedule_data' not in context.bot_data:
            context.bot_data['schedule_data'] = await async_read_schedule_sheet(SCHEDULE_SHEET_URL)
        
        schedule_data = context.bot_data['schedule_data']
        current_date = get_current_date()

        # Оптимизированный поиск с использованием генератора
        today_schedule = next(
            (item for item in schedule_data 
             if 'дата' in item and normalize_table_date(item['дата']) == current_date),
            None
        )

        # Формирование ответа
        response_text = (
            format_schedule_message(today_schedule, schedule_data) 
            if today_schedule 
            else "📭 На сегодня новостей нет!"
        )

        # Асинхронная отправка
        if query:
            await query.answer()
            await context.bot.send_message(
                chat_id=message.chat_id,
                text=response_text,
                parse_mode='Markdown'
            )
        else:
            await message.reply_text(response_text, parse_mode='Markdown')

        logger.info(f"News processed for {current_date}")

    except Exception as e:
        logger.error(f"Error in handle_news: {str(e)}", exc_info=True)
        error_msg = "⚠️ Не удалось загрузить расписание. Попробуйте позже."
        if update.callback_query:
            await update.callback_query.answer(error_msg, show_alert=True)
        else:
            await message.reply_text(error_msg)
