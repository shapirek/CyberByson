import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from bot.common import load_users_data_async
from bot.config import REQUEST_EQUIPMENT
from .env import CHANNEL_LINK_PART
from bot.services.send_messages.plea import send_plea_to_channel_async
from bot.services.formatters import format_message_with_signature_async
from bot.utils.keyboards.staff_menu import show_staff_menu

logger = logging.getLogger(__name__)


async def handle_request_equipment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Начинает сценарий запроса техники: спрашиваем у пользователя детали.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Укажите, какая техника необходима, когда и куда её принести:"
    )
    return REQUEST_EQUIPMENT


async def handle_equipment_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Получаем текст запроса техники, публикуем его в канал,
    а затем рассылаем всем технозондерам ссылку на тред.
    """
    # 1) Загрузка users_data
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    users = context.bot_data['users_data']

    # 2) Сохраняем и валидируем данные
    equipment_request = update.message.text
    context.user_data['equipment_request'] = equipment_request

    sender_code = str(context.user_data.get('code', ''))
    sender = next((u for u in users if str(u.get('код')) == sender_code), None)
    if not sender:
        await update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # 3) Отправляем plea в канал (возвращает {'message_id', 'thread_id'})
    channel_data = await send_plea_to_channel_async(
        context,
        message_text=equipment_request,
        sender_name=sender['имя'],
        sender_surname=sender['фамилия'],
        sender_status=sender['статус'],
        recipient_type='equipment_request'
    )
    if not channel_data:
        await update.message.reply_text("⚠️ Не удалось опубликовать запрос в канал.")
        return ConversationHandler.END

    # 4) Собираем URL треда
    thread_url = (
        f"https://t.me/c/{CHANNEL_LINK_PART}/"
        f"{channel_data['message_id']}?thread={channel_data['thread_id']}"
    )

    # 5) Находим всех технозондеров
    tech_zonders = [u['id'] for u in users if u.get('технозондер') == '1']
    if not tech_zonders:
        await update.message.reply_text("❌ Нет технозондеров для рассылки!")
        return await show_staff_menu(update, context)

    # 6) Формируем текст и клавиатуру
    formatted = await format_message_with_signature_async(
        equipment_request,
        sender['имя'],
        sender['фамилия'],
        sender['статус'],
        recipient_type='equipment_request'
    )
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("Подставить техноплечо 🦾", url=thread_url)
    ]])

    # 7) Рассылка пакетами по 30/сек
    send_tasks = [
        context.bot.send_message(chat_id=int(uid), text=formatted, reply_markup=reply_markup)
        for uid in tech_zonders
    ]
    for i in range(0, len(send_tasks), 30):
        await asyncio.gather(*send_tasks[i:i+30])
        if i + 30 < len(send_tasks):
            await asyncio.sleep(1)

    # 8) Сообщаем об успехе и возвращаем меню
    await update.message.reply_text("✅ Запрос на технику отправлен всем технозондерам!")
    return await show_staff_menu(update, context)
