import logging
from typing import Optional, Dict

from telegram.ext import ContextTypes
from telegram import ParseMode

from bot.config import CHANNEL_ID
from bot.services.formatters import (
    format_message_with_signature_async,
    generate_unique_id,
)
 
logger = logging.getLogger(__name__)


async def send_plea_to_channel_async(
    context: ContextTypes.DEFAULT_TYPE,
    message_text: str,
    sender_name: str,
    sender_surname: str,
    sender_status: str,
    recipient_type: str,
    **kwargs
) -> Optional[Dict[str, int]]:
    """
    Асинхронно отправляет «объявление» (plea) в канал и возвращает его ID/thread_id.
    """
    try:
        # 1) Форматируем текст под Markdown
        formatted_message = await format_message_with_signature_async(
            message_text,
            sender_name,
            sender_surname,
            sender_status,
            recipient_type,
            **kwargs
        )

        # 2) Шлём в канал
        sent = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=formatted_message,
            parse_mode=ParseMode.MARKDOWN
        )

        # 3) Структурируем данные о сообщении
        message_data = {
            'message_id': sent.message_id,
            'thread_id': sent.message_id  # для plea мы просто используем тот же ID
        }

        # 4) Генерируем уникальный ключ и сохраняем в user_data
        unique_id = generate_unique_id()
        context.user_data['last_channel_message'] = message_data
        context.user_data['current_message_id'] = unique_id

        logger.info(f"Plea sent to channel. ID={sent.message_id}")
        return message_data

    except Exception as e:
        logger.error(f"Failed to send plea to channel: {e}", exc_info=True)
        return None
