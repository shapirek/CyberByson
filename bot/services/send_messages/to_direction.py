import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.common import load_users_data_async
from bot.services.filters import get_receivers_async
from bot.services.send_messages.signatures import send_message_with_signature

logger = logging.getLogger(__name__)


async def send_message_to_direction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Рассылает сообщение всем пользователям из выбранного направления.
    """
    # 1) Загрузка и кэш users_data
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    users_data = context.bot_data['users_data']

    # 2) Подготовка данных
    message_text = context.user_data.get('message_text', '')
    direction = context.user_data.get('selected_direction', '')
    sender_code = str(context.user_data.get('code', ''))
    sender = next((u for u in users_data if str(u.get('код')) == sender_code), None)

    # 3) Выбор целевого метода отправки ошибок/успеха
    target = update.effective_message  # подходит для message и callback_query

    # 4) Проверяем отправителя
    if not sender:
        await target.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # 5) Получаем список получателей по фильтру 'direction'
    receivers = await get_receivers_async(
        users_data=users_data,
        recipient_type='direction',
        sender_id=sender['id'],
        direction=direction
    )

    if not receivers:
        await target.reply_text("❌ Нет сотрудников в этом направлении!")
        return ConversationHandler.END

    # 6) Асинхронная пакетная рассылка
    async def _send_to(uid: str):
        try:
            await send_message_with_signature(
                context=context,
                chat_id=int(uid),
                message_text=message_text,
                sender_name=sender['имя'],
                sender_surname=sender['фамилия'],
                sender_status=sender['статус'],
                recipient_type='direction',
                direction=direction
            )
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {uid}: {e}", exc_info=True)

    for i in range(0, len(receivers), 30):
        batch = receivers[i : i + 30]
        await asyncio.gather(*[_send_to(uid) for uid in batch])
        if i + 30 < len(receivers):
            await asyncio.sleep(1)

    # 7) Подтверждаем успешную рассылку
    await target.reply_text("✅ Сообщения отправлены!")
    return ConversationHandler.END
