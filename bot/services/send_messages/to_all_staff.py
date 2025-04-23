import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.common import load_users_data_async
from bot.services.filters import get_receivers_async
from bot.services.send_messages.send_message_with_signature import send_message_with_signature

logger = logging.getLogger(__name__)


async def send_message_to_all_staff(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Асинхронно рассылает сообщение всем сотрудникам (all_staff),
    используя форматирование с подписью.
    """
    # 1) Загрузка и кэширование users_data
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    users_data = context.bot_data['users_data']

    # 2) Подготовка текста и поиск отправителя
    message_text = context.user_data.get('message_text', '')
    sender_code = str(context.user_data.get('code', ''))
    sender = next((u for u in users_data if str(u.get('код')) == sender_code), None)

    if not sender:
        err = "❌ Ошибка: отправитель не найден!"
        target = update.callback_query.message if update.callback_query else update.message
        await target.reply_text(err)
        return ConversationHandler.END

    # 3) Фильтрация получателей
    receivers = await get_receivers_async(
        users_data=users_data,
        recipient_type='all_staff',
        sender_id=sender['id']
    )

    if not receivers:
        err = "❌ Нет сотрудников для рассылки!"
        target = update.callback_query.message if update.callback_query else update.message
        await target.reply_text(err)
        return ConversationHandler.END

    # 4) Асинхронная пакетная рассылка
    async def _send_to(user_id: str):
        try:
            await send_message_with_signature(
                context=context,
                chat_id=int(user_id),
                message_text=message_text,
                sender_name=sender['имя'],
                sender_surname=sender['фамилия'],
                sender_status=sender['статус'],
                recipient_type='all_staff'
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке сотруднику {user_id}: {e}", exc_info=True)

    # Пакеты по 30 сообщений/сек
    for i in range(0, len(receivers), 30):
        batch = receivers[i:i+30]
        await asyncio.gather(*[_send_to(uid) for uid in batch])
        if i + 30 < len(receivers):
            await asyncio.sleep(1)

    # 5) Подтверждение успешной рассылки
    success = "✅ Сообщения отправлены!"
    target = update.callback_query.message if update.callback_query else update.message
    await target.reply_text(success)

    return ConversationHandler.END
