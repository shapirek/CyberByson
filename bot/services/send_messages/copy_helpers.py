import logging
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.common import load_users_data_async
from bot.env import CHANNEL_LINK_PART
from bot.services.formatters import generate_tags

logger = logging.getLogger(__name__)


async def send_copy_to_sender(
    update, 
    context: ContextTypes.DEFAULT_TYPE, 
    message_text: str
) -> None:
    """
    Асинхронно отправляет копию сообщения с кнопками и закрепляет её.
    """
    # 1) Загрузить и закешировать users_data
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    users = context.bot_data['users_data']

    # 2) Найти отправителя по коду
    sender_code = str(context.user_data.get('code', ''))
    sender = next((u for u in users if str(u.get('код')) == sender_code), None)
    if not sender:
        return

    # 3) Получить metadata последнего сообщения
    unique_id = context.user_data.get('current_message_id')
    if not unique_id:
        return
    message_data = context.user_data.get(unique_id, {})
    channel_id = message_data.get('channel_message_id')
    thread_id  = message_data.get('thread_id')
    if not channel_id or not thread_id:
        return

    # 4) Собрать URL треда
    thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{channel_id}?thread={thread_id}"

    # 5) Отправить копию с кнопками и закрепить
    try:
        sent = await context.bot.send_message(
            chat_id=int(sender['id']),
            text=(
                "📨 КОПИЯ СООБЩЕНИЯ 📨\n"
                f"{generate_tags(message_text)}\n\n"
                f"{message_text}\n\n"
                f"С уважением,\n{sender['имя']} {sender['фамилия']}"
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Ответы", url=thread_url),
                InlineKeyboardButton(
                    "Проблема решена!", 
                    callback_data=f"problem_solved_{unique_id}"
                )
            ]])
        )
        await context.bot.pin_chat_message(
            chat_id=int(sender['id']),
            message_id=sent.message_id
        )
        # Обновить metadata с group_message_id
        context.user_data.setdefault(unique_id, {})['group_message_id'] = sent.message_id

    except Exception as e:
        logger.error(f"Ошибка отправки копии с кнопками: {e}", exc_info=True)


async def send_plain_copy_to_sender(
    update, 
    context: ContextTypes.DEFAULT_TYPE, 
    message_text: str
) -> None:
    """
    Асинхронно отправляет копию сообщения без кнопок.
    """
    # 1) Загрузить и закешировать users_data
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    users = context.bot_data['users_data']

    # 2) Найти отправителя
    sender_code = str(context.user_data.get('code', ''))
    sender = next((u for u in users if str(u.get('код')) == sender_code), None)
    if not sender:
        return

    # 3) Отправить копию без кнопок
    try:
        await context.bot.send_message(
            chat_id=int(sender['id']),
            text=(
                "📨 КОПИЯ СООБЩЕНИЯ 📨\n"
                f"{generate_tags(message_text)}\n\n"
                f"{message_text}\n\n"
                f"С уважением,\n{sender['имя']} {sender['фамилия']}"
            )
        )
    except Exception as e:
        logger.error(f"Ошибка отправки plain-копии: {e}", exc_info=True)
