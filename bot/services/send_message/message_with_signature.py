from telegram.ext import CallbackContext
from typing import Optional, Any
from your_utils import format_message_with_signature  # Утилита форматирования
import asyncio  # Для асинхронной версии
import logging  # Для логирования


async def send_message_with_signature(
    context: CallbackContext,
    chat_id: str,
    message_text: str,
    sender_name: str,
    sender_surname: str,
    sender_status: str,
    recipient_type: Optional[str] = None,
    **kwargs
) -> None:
    """
    Асинхронно отправляет форматированное сообщение с подписью.
    
    Args:
        context: Контекст бота
        chat_id: ID чата для отправки
        message_text: Текст сообщения
        sender_name: Имя отправителя
        sender_surname: Фамилия отправителя
        sender_status: Статус отправителя
        recipient_type: Тип получателя (опционально)
        **kwargs: Дополнительные параметры
    """
    try:
        # Асинхронное форматирование сообщения
        formatted_message = await format_message_with_signature_async(
            message_text,
            sender_name,
            sender_surname,
            sender_status,
            recipient_type,
            **kwargs
        )
        
        # Асинхронная отправка
        await context.bot.send_message(
            chat_id=chat_id,
            text=formatted_message,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения: {str(e)}")
        raise  # Пробрасываем исключение для обработки выше
