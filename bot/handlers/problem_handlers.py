import re
import logging

from telegram import Update
from telegram.ext import ContextTypes

from .env import CHANNEL_ID, GROUP_ID
from bot.common import load_users_data_async

logger = logging.getLogger(__name__)


async def handle_problem_solved_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Ловит callback_data вида 'problem_solved_{unique_id}' и 
    перенаправляет на handle_problem_solved.
    """
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    logger.debug(f"Callback data: {data}")

    m = re.match(r"^problem_solved_(?P<uid>[0-9a-fA-F\-]+)$", data)
    if not m:
        return

    unique_id = m.group("uid")
    await handle_problem_solved(update, context, unique_id)


async def handle_problem_solved(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    unique_id: str
) -> None:
    """
    Удаляет сообщения из канала и группы, открепляет копию пользователю,
    и изменяет текст кнопки на 'Проблема решена'.
    """
    query = update.callback_query
    await query.answer()

    # 1) Получаем metadata
    message_data = context.user_data.get(unique_id, {})
    if not message_data:
        await query.edit_message_text("❌ Ошибка: данные сообщения не найдены.")
        return

    # 2) Удаляем из канала
    channel_msg_id = message_data.get("channel_message_id")
    if channel_msg_id:
        try:
            await context.bot.delete_message(
                chat_id=CHANNEL_ID,
                message_id=channel_msg_id
            )
        except Exception as e:
            logger.error(f"Ошибка удаления сообщения из канала: {e}", exc_info=True)

    # 3) Удаляем из группы
    group_msg_id = message_data.get("group_message_id")
    if group_msg_id:
        try:
            await context.bot.delete_message(
                chat_id=GROUP_ID,
                message_id=group_msg_id
            )
        except Exception as e:
            logger.error(f"Ошибка удаления сообщения из группы: {e}", exc_info=True)

    # 4) Открепляем у отправителя
    if group_msg_id:
        # убедимся, что users_data загружены
        if "users_data" not in context.bot_data:
            context.bot_data["users_data"] = await load_users_data_async()
        users = context.bot_data["users_data"]

        sender_code = str(context.user_data.get("code", ""))
        sender = next((u for u in users if str(u.get("код")) == sender_code), None)
        if sender:
            try:
                await context.bot.unpin_chat_message(
                    chat_id=int(sender["id"]),
                    message_id=group_msg_id
                )
                logger.debug(f"Сообщение {group_msg_id} откреплено.")
            except Exception as e:
                logger.error(f"Ошибка открепления сообщения: {e}", exc_info=True)

    # 5) Обновляем текст кнопки
    try:
        await query.edit_message_text(
            "✅ Проблема отмечена как решенная. "
            "Сообщения удалены и откреплены."
        )
    except Exception as e:
        logger.error(f"Ошибка редактирования сообщения: {e}", exc_info=True)

    # 6) Чистим context.user_data
    context.user_data.pop(unique_id, None)
