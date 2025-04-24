import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.utils.keyboards.message_options import show_message_options
from bot.config import INPUT_MESSAGE

logger = logging.getLogger(__name__)


async def handle_team_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает выбор команды из inline-меню:
    – если data.startswith('team_'), сохраняет команду и переходит к вводу сообщения;
    – если 'back_to_message_options', возвращает в меню выбора получателей;
    – иначе выводит ошибку.
    """
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    # Выбрали команду
    if data.startswith("team_"):
        team = data.split("_", 1)[1]
        context.user_data["selected_team"]   = team
        context.user_data["recipient_type"]  = "team"
        await query.edit_message_text(f"Введите сообщение для команды {team}:")
        return INPUT_MESSAGE

    # Назад к меню выбора получателей
    if data == "back_to_message_options":
        return await show_message_options(update, context)

    # Неизвестная команда
    logger.warning(f"Unknown team choice callback_data: {data}")
    await query.edit_message_text("❌ Неизвестная команда.")
    return ConversationHandler.END
