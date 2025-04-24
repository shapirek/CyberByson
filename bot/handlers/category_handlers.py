import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.common import load_users_data_async
from bot.utils.keyboards.main_menu import show_main_menu
from bot.utils.keyboards.parents_menu import show_parents_menu
from bot.utils.keyboards.students_menu import show_students_menu
from bot.config import CODE_INPUT, PARENTS_ACTION, STUDENTS_ACTION

logger = logging.getLogger(__name__)


async def handle_category(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает выбор категории из главного меню:
    – Завершить диалог
    – Родители
    – Школьники
    – Сотрудники
    """
    text = update.message.text

    # 1) Завершение
    if text == "Завершить диалог":
        await update.message.reply_text("Диалог завершён. До новых встреч!")
        return ConversationHandler.END

    # 2) Родители
    if text == "Родители":
        return await show_parents_menu(update, context)

    # 3) Школьники
    if text == "Школьники":
        return await show_students_menu(update, context)

    # 4) Сотрудники
    if text == "Сотрудники":
        try:
            # Асинхронно загружаем таблицу пользователей
            context.bot_data['users_data'] = await load_users_data_async()
            logger.info("Данные пользователей загружены для сотрудников")
            await update.message.reply_text("Укажите Ваш код доступа:")
            return CODE_INPUT
        except Exception as e:
            logger.error(f"Ошибка загрузки данных сотрудников: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
            return ConversationHandler.END

    # 5) Неизвестная команда
    await update.message.reply_text("⚠️ Пожалуйста, выберите опцию из меню.")
    return ConversationHandler.END
