from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

import logging
logger = logging.getLogger(__name__)

from your_data_module import users_data  # или как у тебя называется

import asyncio
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


async def send_message_to_director(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            await update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    receivers = [user['id'] for user in users_data
                 if user.get('статус') == '0' and user.get('id') and user['id'] != sender['id']]

    if not receivers:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Нет сотрудников в дирекции!")
        else:
            await update.message.reply_text("❌ Нет сотрудников в дирекции!")
    else:
        async def send(uid):
            try:
                await send_message_with_signature(
                    context, uid, message_text,
                    sender['имя'], sender['фамилия'], sender['статус'],
                    recipient_type='director'
                )
            except Exception as e:
                logger.warning(f"Ошибка отправки сообщения {uid}: {e}")

        # Распараллеливаем отправку сообщений
        await asyncio.gather(*(send(uid) for uid in receivers))

        if update.callback_query:
            await update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            await update.message.reply_text("✅ Сообщения отправлены!")

    return ConversationHandler.END
