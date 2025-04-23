import logging
from typing import Optional

from telegram.ext import ContextTypes
from telegram import ParseMode

from .env import CHANNEL_ID
from bot.services.formatters import (
    format_message_with_signature_async,
    generate_unique_id,
)

logger = logging.getLogger(__name__)


async def send_message_to_channel(
    context: ContextTypes.DEFAULT_TYPE,
    message_text: str,
    sender_name: str,
    sender_surname: str,
    sender_status: str,
    recipient_type: str,
    **kwargs
) -> Optional[dict]:
    """
    Асинхронно публикует сообщение в канал (или в тред) и сохраняет его metadata.

    Возвращает словарь с полями:
      - message_id
      - thread_id
      - group_message_id (None для каналов)
    """
    try:
        # 1) Форматируем текст
        formatted = await format_message_with_signature_async(
            message_text,
            sender_name,
            sender_surname,
            sender_status,
            recipient_type,
            **kwargs
        )

        # 2) Определяем reply_to (thread) — если есть в user_data
        reply_to = context.user_data.get('thread_id')

        # 3) Шлём в канал
        sent = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=formatted,
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=reply_to  # None автоматически игнорируется
        )

        # 4) Готовим и сохраняем metadata
        metadata = {
            'message_id': sent.message_id,
            'thread_id': sent.message_id,
            'group_message_id': None,
        }
        unique_key = generate_unique_id()
        context.user_data[unique_key] = metadata
        context.user_data['current_message_id'] = unique_key

        logger.info(f"Published to channel: {sent.message_id} (reply_to={reply_to})")
        return metadata

    except Exception as e:
        logger.error(f"Failed to send message to channel: {e}", exc_info=True)
        return None
