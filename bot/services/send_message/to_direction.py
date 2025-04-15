from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import asyncio


async def send_message_to_direction(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    direction = context.user_data.get('selected_direction')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            await update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    receivers = [user['id'] for user in users_data
                 if user.get('направление') == direction and user['id'] != sender['id']]

    if not receivers:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Нет сотрудников в этом направлении!")
        else:
            await update.message.reply_text("❌ Нет сотрудников в этом направлении!")
    else:
        async def send(uid):
            try:
                await send_message_with_signature(
                    context, uid, message_text, sender['имя'], sender['фамилия'], sender['статус'], direction
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {uid}: {e}")

        await asyncio.gather(*(send(uid) for uid in receivers))

        if update.callback_query:
            await update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            await update.message.reply_text("✅ Сообщения отправлены!")

    return ConversationHandler.END
