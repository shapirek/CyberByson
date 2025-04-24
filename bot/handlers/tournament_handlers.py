import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.utils.keyboards.message_options import show_message_options
from bot.config import INPUT_MESSAGE

logger = logging.getLogger(__name__)


async def handle_tournament_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает выбор турнира из inline-меню:
    – если data.startswith('tournament_'), сохраняет турнир и переходит к вводу сообщения;
    – если 'back_to_message_options', возвращает в меню выбора получателей;
    – иначе выводит ошибку.
    """
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    # Выбрали турнир
    if data.startswith("tournament_"):
        tournament = data.split("_", 1)[1]
        context.user_data["selected_tournament"] = tournament
        context.user_data["recipient_type"]       = "tournament_judges"
        await query.edit_message_text(f"Введите сообщение для судей {tournament}:")
        return INPUT_MESSAGE

    # Назад к меню выбора получателей
    if data == "back_to_message_options":
        return await show_message_options(update, context)

    # Неизвестная команда
    logger.warning(f"Unknown tournament choice callback_data: {data}")
    await query.edit_message_text("❌ Неизвестный турнир.")
    return ConversationHandler.END
