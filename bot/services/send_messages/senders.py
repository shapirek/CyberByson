import asyncio
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from bot.common import load_users_data_async
from bot.env import CHANNEL_LINK_PART
from bot.config import PARENTS_ACTION, DIRECTOR_ACTION, STAFF_ACTION, STUDENTS_ACTION, CHOOSE_RECIPIENT
from bot.services.send_messages.channel import send_message_to_channel
from bot.services.send_messages.copy_helpers import send_copy_to_sender
from bot.services.formatters import format_message_with_signature_async

logger = logging.getLogger(__name__)


async def send_message_with_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    recipient_type: str,
    **kwargs
) -> int:
    # 1) Загрузка users_data (кеш в bot_data)
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    users_data = context.bot_data['users_data']

    # 2) Собираем входные данные
    message_text = context.user_data.get('message_text', '')
    sender_code  = str(context.user_data.get('code', ''))
    sender = next((u for u in users_data if str(u.get('код')) == sender_code), None)

    # 3) Если не нашли — сообщаем и выходим
    if not sender:
        err = "❌ Отправитель не найден!"
        if update.callback_query:
            await update.callback_query.edit_message_text(err)
        else:
            await update.message.reply_text(err)
        return ConversationHandler.END

    try:
        # 4) Публикуем в канал и берём thread-id
        channel_data = await send_message_to_channel_async(
            context, message_text, 
            sender['имя'], sender['фамилия'], sender['статус'],
            recipient_type, **kwargs
        )
        thread_url = (
            f"https://t.me/c/{CHANNEL_LINK_PART}/"
            f"{channel_data['message_id']}?thread={channel_data['thread_id']}"
        )

        # 5) Форматируем сообщение для пользователей
        formatted_msg = await format_message_with_signature_async(
            message_text, sender['имя'], sender['фамилия'],
            sender['статус'], recipient_type, **kwargs
        )

        # 6) Подключаем кнопку
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Подставить плечо 💪", url=thread_url)]]
        )

        # 7) Получаем список получателей
        from bot.services.filters import get_receivers_async
        users_ids = await get_receivers_async(
            users_data, recipient_type, sender['id'], **kwargs
        )

        # 8) Шлём пакетами по 30/сек
        tasks = [
            context.bot.send_message(chat_id=uid, text=formatted_msg, reply_markup=reply_markup)
            for uid in users_ids
        ]
        for i in range(0, len(tasks), 30):
            await asyncio.gather(*tasks[i:i+30])
            if i + 30 < len(tasks):
                await asyncio.sleep(1)

        # 9) Дублируем себе
        await send_copy_to_sender_async(update, context, message_text)

        # 10) Возвращаем следующее состояние (пример)
        return CHOOSE_RECIPIENT

    except Exception as e:
        logger.error("Ошибка отправки с кнопкой:", exc_info=e)
        err = "⚠️ Не удалось отправить сообщения."
        if update.callback_query:
            await update.callback_query.edit_message_text(err)
        else:
            await update.message.reply_text(err)
        return ConversationHandler.END
