import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.common import load_users_data_async
from bot.config import INPUT_MESSAGE
from bot.utils.keyboards.director_menu import show_director_menu
from bot.utils.keyboards.staff_menu import show_staff_menu

logger = logging.getLogger(__name__)


async def handle_direction_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает выбор направления из inline-меню:
    – «Назад» возвращает в меню дирекции или сотрудников
    – иначе сохраняет выбранное направление и переходит к вводу сообщения
    """
    query = update.callback_query
    await query.answer()
    choice = query.data

    # Если нажали «Назад»
    if choice == 'back_to_director':
        # Загрузим users_data, если ещё не загружены
        if 'users_data' not in context.bot_data:
            context.bot_data['users_data'] = await load_users_data_async()
        users = context.bot_data['users_data']

        code = str(context.user_data.get('code', ''))
        sender = next((u for u in users if str(u.get('код')) == code), None)
        if not sender:
            await query.edit_message_text("❌ Ошибка: отправитель не найден!")
            return ConversationHandler.END

        # Возвращаем в нужное меню
        if sender.get('статус') == '0':
            return await show_director_menu(update, context)
        else:
            return await show_staff_menu(update, context)

    # Иначе — выбрали конкретное направление
    context.user_data['selected_direction'] = choice
    context.user_data['recipient_type']    = 'direction'

    await query.edit_message_text("Введите послание:")
    return INPUT_MESSAGE
