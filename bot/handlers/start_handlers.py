from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.utils.keyboards.main_menu import show_main_menu

logger = logging.getLogger(__name__)

async def handle_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает команду /start: очищаем user_data,
    шлём приветствие и показываем главное меню.
    Возвращаем ConversationHandler.END, чтобы диалог был «готов»
    к дальнейшим кнопкам.
    """
    logger.info(f"handle_start вызван для {update.effective_user.id}")
    context.user_data.clear()
    await update.message.reply_text("Приветствуем, кожаный мешок!")
    await show_main_menu(update, context)
    return ConversationHandler.END
