from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.keyboards.main_menu import show_main_menu

async def handle_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатываем команду /start: показываем главное меню.
    """
    # Сбрасываем данные пользователя, если нужно
    context.user_data.clear()

    # Приветствие (по желанию)
    await update.message.reply_text("Привет! Это бот, созданный для КЛШ с целью упростить некоторые аспекты летней школы!")

    # Показываем главное меню
    return await show_main_menu(update, context)
