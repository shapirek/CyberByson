import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.common import load_users_data_async
from bot.services.filters import get_receivers_async
from bot.services.send_messages.send_message_with_signature import send_message_with_signature

logger = logging.getLogger(__name__)


async def send_message_to_team(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Рассылает сообщение всем вожатым указанной команды.
    """
    # 1) Загрузка и кеш пользователей
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    users_data = context.bot_data['users_data']

    # 2) Извлечение текста, команды и отправителя
    message_text = context.user_data.get('message_text', '')
    team = context.user_data.get('selected_team', '')
    sender_code = str(context.user_data.get('code', ''))
    sender = next((u for u in users_data if str(u.get('код')) == sender_code), None)

    # 3) Точка для ответов (message или callback)
    target = update.effective_message

    if not sender:
        await target.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # 4) Выбор получателей по фильтру 'team'
    receivers = await get_receivers_async(
        users_data=users_data,
        recipient_type='team',
        sender_id=sender['id'],
        team=team
    )

    if not receivers:
        await target.reply_text(f"❌ Нет вожатых в команде {team}!")
        return ConversationHandler.END

    # 5) Асинхронная пакетная рассылка
    async def _send_to(uid: str):
        try:
            await send_message_with_signature(
                context=context,
                chat_id=int(uid),
                message_text=message_text,
                sender_name=sender['имя'],
                sender_surname=sender['фамилия'],
                sender_status=sender['статус'],
                recipient_type='team',
                team=team
            )
        except Exception as e:
            logger.warning(f"Ошибка при отправке пользователю {uid}: {e}", exc_info=True)

    for i in range(0, len(receivers), 30):
        batch = receivers[i : i + 30]
        await asyncio.gather(*[_send_to(uid) for uid in batch])
        if i + 30 < len(receivers):
            await asyncio.sleep(1)

    # 6) Подтверждение успешной рассылки
    await target.reply_text("✅ Сообщения отправлены!")
    return ConversationHandler.END
