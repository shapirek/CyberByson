import logging
from typing import Optional

from telegram.ext import ContextTypes
from telegram import ParseMode

from bot.services.formatters import format_message_with_signature_async

logger = logging.getLogger(__name__)


async def send_message_with_signature(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_text: str,
    sender_name: str,
    sender_surname: str,
    sender_status: str,
    recipient_type: Optional[str] = None,
    **kwargs
) -> None:
    """
    Асинхронно форматирует и отправляет сообщение с подписью.
    """
    try:
        # Форматируем текст асинхронно
        formatted_message = await format_message_with_signature_async(
            message_text,
            sender_name,
            sender_surname,
            sender_status,
            recipient_type,
            **kwargs
        )

        # Отправляем сообщение в указанный чат
        await context.bot.send_message(
            chat_id=chat_id,
            text=formatted_message,
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        logger.error(f"Ошибка отправки сообщения с подписью: {e}", exc_info=True)
        # Пробрасываем, чтобы верхний уровень мог прервать ConversationHandler или отреагировать иначе
        raise
