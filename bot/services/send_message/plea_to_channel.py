from telegram.ext import CallbackContext
from your_utils import format_message_with_signature, generate_unique_id  # Ваши утилиты
from your_config import CHANNEL_ID  # Конфигурация
import asyncio  # Для асинхронной версии
import logging  # Для логирования
from typing import Optional, Dict, Any


async def send_plea_to_channel_async(
    context: CallbackContext,
    message_text: str,
    sender_name: str,
    sender_surname: str,
    sender_status: str,
    recipient_type: str,
    **kwargs
) -> Optional[Dict[str, int]]:
    """
    Асинхронно отправляет сообщение в канал и возвращает данные сообщения.
    
    Args:
        context: Контекст бота
        message_text: Текст сообщения
        sender_name: Имя отправителя
        sender_surname: Фамилия отправителя
        sender_status: Статус отправителя
        recipient_type: Тип получателя
        **kwargs: Дополнительные параметры
        
    Returns:
        Словарь с ID сообщения и thread_id или None при ошибке
    """
    try:
        # Асинхронное форматирование
        formatted_message = await format_message_with_signature_async(
            message_text,
            sender_name,
            sender_surname,
            sender_status,
            recipient_type,
            **kwargs
        )
        
        # Асинхронная отправка
        sent_message = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=formatted_message
        )
        
        # Генерация и сохранение данных
        message_data = {
            'channel_message_id': sent_message.message_id,
            'thread_id': sent_message.message_id  # Используем message_id как thread_id
        }
        
        unique_id = generate_unique_id()
        context.user_data.update({
            unique_id: message_data,
            'current_message_id': unique_id
        })
        
        logger.info(f"Сообщение отправлено в канал. ID: {sent_message.message_id}")
        return message_data
        
    except Exception as e:
        logger.error(f"Ошибка отправки в канал: {str(e)}", exc_info=True)
        return None
