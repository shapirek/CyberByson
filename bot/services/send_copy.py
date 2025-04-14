from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import asyncio
from typing import Optional
from your_config import CHANNEL_LINK_PART  # Импорт констант из конфига
from your_utils import generate_tags  # Импорт утилиты для генерации тегов


async def send_copy_to_sender(update: Update, context: CallbackContext, message_text: str) -> None:
    """
    Асинхронно отправляет копию сообщения с кнопками и закрепляет его.
    """
    # Кэширование данных пользователей
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    
    sender = next((u for u in context.bot_data['users_data'] 
                 if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        return

    unique_id = context.user_data.get('current_message_id')
    if not unique_id:
        return

    message_data = context.user_data.get(unique_id, {})
    if not (channel_message_id := message_data.get('channel_message_id')) or not (thread_id := message_data.get('thread_id')):
        return

    thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{channel_message_id}?thread={thread_id}"
    
    # Асинхронная отправка и закрепление
    try:
        sent_message = await context.bot.send_message(
            chat_id=sender['id'],
            text=f"📨 КОПИЯ СООБЩЕНИЯ 📨\n{generate_tags(message_text)}\n\n{message_text}\n\nС уважением,\n{sender['имя']} {sender['фамилия']}",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Ответы", url=thread_url),
                    InlineKeyboardButton("Проблема решена!", callback_data=f'problem_solved_{unique_id}')
                ]
            ])
        )
        
        await context.bot.pin_chat_message(chat_id=sender['id'], message_id=sent_message.message_id)
        context.user_data.setdefault(unique_id, {}).update({'group_message_id': sent_message.message_id})

    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")

async def send_plain_copy_to_sender(update: Update, context: CallbackContext, message_text: str) -> None:
    """
    Асинхронно отправляет копию без кнопок.
    """
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    
    if not (sender := next((u for u in context.bot_data['users_data'] 
                          if str(u['код']) == context.user_data.get('code')), None)):
        return

    try:
        await context.bot.send_message(
            chat_id=sender['id'],
            text=f"📨 КОПИЯ СООБЩЕНИЯ 📨\n{generate_tags(message_text)}\n\n{message_text}\n\nС уважением,\n{sender['имя']} {sender['фамилия']}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
