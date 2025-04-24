import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.common import load_users_data_async
from bot.utils.keyboards.main_menu import show_main_menu
from bot.utils.keyboards.director_menu import show_director_menu
from bot.utils.keyboards.staff_menu import show_staff_menu

logger = logging.getLogger(__name__)


async def handle_code_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Проверяет введённый код доступа, сохраняет его в user_data
    и перенаправляет пользователя в нужное меню.
    """
    input_code = update.message.text.strip()

    # 1) Загрузим список пользователей (с кешем в bot_data)
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    users = context.bot_data['users_data']

    # 2) Ищем пользователя по коду
    user = next((u for u in users if str(u.get('код')) == input_code), None)
    if not user:
        await update.message.reply_text("❌ Неверный код доступа!")
        await show_main_menu(update, context)
        return ConversationHandler.END

    # 3) Сохраняем код в контекст и выбираем меню по статусу
    context.user_data['code'] = input_code
    status = user.get('статус')

    if status == '0':
        # Дирекция
        return await show_director_menu(update, context)
    elif status == '1':
        # Сотрудники
        return await show_staff_menu(update, context)
    else:
        # Неизвестный статус
        await update.message.reply_text("⚠️ Неизвестный статус пользователя!")
        await show_main_menu(update, context)
        return ConversationHandler.END
