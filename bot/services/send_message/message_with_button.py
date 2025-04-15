from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import asyncio
from typing import List, Dict, Optional
from your_config import CHANNEL_LINK_PART  # Конфигурационные константы
from your_utils import format_message_with_signature  # Утилиты форматирования
import logging


logger = logging.getLogger(__name__)

async def send_message_with_button(
    update: Update, 
    context: CallbackContext, 
    recipient_type: str, 
    **kwargs
) -> None:
    """Асинхронная отправка сообщений с кнопкой"""
    # Проверка и загрузка данных
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    
    users_data = context.bot_data['users_data']
    message_text = context.user_data.get('message_text')
    
    # Поиск отправителя
    sender = next(
        (u for u in users_data 
         if str(u['код']) == context.user_data.get('code')),
        None
    )
    
    if not sender:
        error_msg = "❌ Ошибка: отправитель не найден!"
        await (update.callback_query.edit_message_text(error_msg) if update.callback_query 
               else update.message.reply_text(error_msg))
        return

    try:
        # Асинхронная отправка в канал
        channel_data = await send_message_to_channel_async(
            context, message_text, sender['имя'], 
            sender['фамилия'], sender['статус'], recipient_type, **kwargs
        )
        
        if not channel_data:
            raise ValueError("Не удалось отправить в канал")
            
        thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{channel_data['message_id']}?thread={channel_data['thread_id']}"
        
        # Форматирование сообщения
        formatted_msg = await format_message_with_signature_async(
            message_text, sender['имя'], sender['фамилия'], 
            sender['статус'], recipient_type, **kwargs
        )
        
        # Создание клавиатуры
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Подставить плечо 💪", url=thread_url)]
        ])
        
        # Получатели (асинхронная фильтрация)
        receivers = await get_receivers_async(
            users_data, recipient_type, sender['id'], **kwargs
        )
        
        # Пакетная отправка
        send_tasks = [
            context.bot.send_message(
                chat_id=user_id,
                text=formatted_msg,
                reply_markup=reply_markup
            )
            for user_id in receivers
        ]
        
        # Ограничение 30 сообщений/сек
        for i in range(0, len(send_tasks), 30):
            await asyncio.gather(*send_tasks[i:i+30])
            if i+30 < len(send_tasks):
                await asyncio.sleep(1)
                
        # Копия отправителю
        await send_copy_to_sender_async(update, context, message_text)
        
    except Exception as e:
        logger.error(f"Ошибка отправки: {str(e)}")
        error_msg = "⚠️ Ошибка при отправке сообщений"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)

async def get_receivers_async(
    users_data: List[Dict], 
    recipient_type: str,
    sender_id: str,
    **kwargs
) -> List[str]:
    """Асинхронный фильтр получателей"""
    filters = {
        'direction': lambda u: u.get('направление') == kwargs.get('direction'),
        'team': lambda u: u.get('команда') == kwargs.get('team'),
        'director': lambda u: u.get('статус') == '0',
        'all_staff': lambda u: bool(u.get('id')),
        'tournament_judges': lambda u: (
            u.get('судья') == '1' and 
            u.get('направление') in kwargs.get('directions', [])
    }
    
    return [
        str(user['id']) for user in users_data
        if filters.get(recipient_type, lambda _: False)(user) 
        and str(user['id']) != sender_id
    ]
