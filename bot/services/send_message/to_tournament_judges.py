from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

import logging
logger = logging.getLogger(__name__)

import asyncio


async def send_message_to_tournament_judges(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    tournament = context.user_data.get('selected_tournament')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            await update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Определяем направления
    directions_by_tournament = {
        'ФМТ': ['НТН'],
        'ГУТ': ['НФН', 'НОН'],
        'БХТ': ['НЕН']
    }
    directions = directions_by_tournament.get(tournament)

    if not directions:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Неизвестный турнир!")
        else:
            await update.message.reply_text("❌ Неизвестный турнир!")
        return ConversationHandler.END

    # Получаем судей
    receivers = [
        user['id'] for user in users_data
        if user.get('судья') == '1' and user.get('направление') in directions
        and user.get('id') and user['id'] != sender['id']
    ]

    if not receivers:
        msg = f"❌ Нет судей для {tournament}!"
        if update.callback_query:
            await update.callback_query.edit_message_text(msg)
        else:
            await update.message.reply_text(msg)
    else:
        async def send(uid):
            try:
                await send_message_with_signature(
                    context, uid, message_text,
                    sender['имя'], sender['фамилия'], sender['статус'],
                    recipient_type='tournament_judges',
                    tournament=tournament
                )
            except Exception as e:
                logger.warning(f"Ошибка отправки сообщения {uid}: {e}")

        await asyncio.gather(*(send(uid) for uid in receivers))

        confirm = "✅ Сообщения отправлены!"
        if update.callback_query:
            await update.callback_query.edit_message_text(confirm)
        else:
            await update.message.reply_text(confirm)

    return ConversationHandler.END
