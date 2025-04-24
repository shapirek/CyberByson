import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.common import load_users_data_async
from bot.config import INPUT_MESSAGE
from bot.utils.keyboards.director_menu import show_director_menu
from bot.utils.keyboards.staff_menu import show_staff_menu
from bot.utils.keyboards.direction_menu import show_directions_menu
from bot.utils.keyboards.team_leaders_menu import show_team_leaders_menu
from bot.utils.keyboards.tournament_judges_menu import show_tournament_judges_menu

logger = logging.getLogger(__name__)


async def handle_recipient_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает выбор получателя после меню send_message_options.
    """
    query = update.callback_query
    await query.answer()
    choice = query.data

    # «Назад» для участников (дирекция/сотрудники)
    if choice == 'back_to_previous_menu':
        # гарантируем, что users_data загружены
        if 'users_data' not in context.bot_data:
            context.bot_data['users_data'] = await load_users_data_async()
        users = context.bot_data['users_data']

        code = str(context.user_data.get('code', ''))
        sender = next((u for u in users if str(u.get('код')) == code), None)
        if not sender:
            await query.edit_message_text("❌ Ошибка: отправитель не найден!")
            return ConversationHandler.END

        if sender.get('статус') == '0':
            return await show_director_menu(update, context)
        else:
            return await show_staff_menu(update, context)

    # Меню «По подразделениям»
    if choice == 'write_to_department':
        return await show_directions_menu(update, context)

    # Меню «По командам»
    if choice == 'write_to_team_leaders':
        return await show_team_leaders_menu(update, context)

    # Меню «По судьям турнира»
    if choice == 'write_to_tournament_judges':
        return await show_tournament_judges_menu(update, context)

    # Конкретные выборы: назначаем recipient_type и ждём текста
    if choice == 'write_to_director':
        context.user_data['recipient_type'] = 'director'
    elif choice == 'write_to_all_staff':
        context.user_data['recipient_type'] = 'all_staff'
    else:
        # здесь всё остальные callback_data — это строка с чьим-то id или ключом
        context.user_data['recipient'] = choice

    # Универсальный запрос текста
    await query.edit_message_text("Введите послание:")
    return INPUT_MESSAGE
