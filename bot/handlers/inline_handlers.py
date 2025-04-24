import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler

from bot.handlers.auth_handlers      import handle_code_input
from bot.handlers.category_handlers  import handle_category
from bot.handlers.news               import handle_news
from bot.handlers.menu_handlers      import director_announcement, staff_write_message
from bot.handlers.equipment_handlers import handle_request_equipment, handle_equipment_input
from bot.handlers.duty_handlers      import handle_assign_duty, handle_student_info_input, handle_student_choice, handle_duty_text_input
from bot.handlers.response_handlers  import handle_wait_for_response
from bot.handlers.problem_handlers   import handle_problem_solved_button
from bot.handlers.parent_handlers    import handle_parent_call, handle_child_name_input, handle_child_choice, handle_message_for_child_input
from bot.handlers.team_handlers      import handle_team_choice
from bot.handlers.tournament_handlers import handle_tournament_choice
from bot.handlers.direction_handlers import handle_direction_choice
from bot.handlers.recipient_handlers import handle_recipient_choice

from bot.utils.keyboards.main_menu import show_main_menu_in_chat
from bot.common import load_users_data_async
from bot.config import (
    CHANNEL_ID, GROUP_ID,
    INPUT_MESSAGE, INPUT_STUDENT_INFO, INPUT_DUTY_TEXT,
    INPUT_CHILD_NAME, INPUT_MESSAGE_FOR_CHILD,
    CODE_INPUT, WAIT_FOR_RESPONSE,
    PARENTS_ACTION, STUDENTS_ACTION, STAFF_ACTION, DIRECTOR_ACTION,
)

logger = logging.getLogger(__name__)


async def inline_button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Универсальный хендлер для всех inline-кнопок.
    """
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    # 1) problem_solved_… обрабатываем в своём хендлере
    if data.startswith("problem_solved_"):
        return await handle_problem_solved_button(update, context)

    # 2) back_to_main
    if data == "back_to_main":
        await query.edit_message_text("Возвращаемся в главное меню.")
        await show_main_menu_in_chat(context, query.message.chat_id)
        return ConversationHandler.END

    # 3) новости
    if data == "news":
        return await handle_news(update, context)

    # 4) код доступа (если вызывается из menu)
    if data == CODE_INPUT:
        return await handle_code_input(update, context)

    # 5) категория «дирекция/сотрудники/…»  
    if data in {"back_to_director", "back_to_staff", "back_to_parents", "back_to_students"}:
        # просто посылаем нужное меню
        if data == "back_to_director":
            return await director_announcement(update, context)  # или show_director_menu
        if data == "back_to_staff":
            return await staff_write_message(update, context)    # или show_staff_menu
        if data == "back_to_parents":
            from bot.handlers.menu_handlers import staff_write_message  # пример
            return await staff_write_message(update, context)
        # … аналогично для студентов
        return ConversationHandler.END

    # 6) назначение наряда
    if data == "assign_duty":
        return await handle_assign_duty(update, context)

    # 7) запрос техники
    if data == "request_equipment":
        return await handle_request_equipment(update, context)

    # 8) меню сообщений (дирекция/сотрудники)
    if data == "director_announcement":
        return await director_announcement(update, context)
    if data == "staff_write_message":
        return await staff_write_message(update, context)

    # 9) возврат к выбору получателя
    if data == "back_to_previous_menu":
        return await handle_recipient_choice(update, context)

    # 10) ожидание ответа — “да/нет”
    if data in {"wait_for_response_yes", "wait_for_response_no"}:
        return await handle_wait_for_response(update, context)

    # 11) родители → звонок ребёнку
    if data == "parent_call":
        return await handle_parent_call(update, context)

    # 12) выбор ребёнка
    if data.startswith("select_child_"):
        return await handle_child_choice(update, context)

    # 13) ввод сообщения для ребёнка
    if data == INPUT_MESSAGE_FOR_CHILD:
        return await handle_message_for_child_input(update, context)

    # 14) выбор команды / турнира / направления
    if data.startswith("team_"):
        return await handle_team_choice(update, context)
    if data.startswith("tournament_"):
        return await handle_tournament_choice(update, context)
    if data.startswith("back_to_message_options"):
        from bot.handlers.team_handlers import handle_team_choice
        return await handle_team_choice(update, context)
    if data.startswith("write_to_department"):
        return await handle_direction_choice(update, context)

    # 15) выбор получателя
    if data in {"write_to_director", "write_to_all_staff"}:
        return await handle_recipient_choice(update, context)
    if data.startswith("write_to_department") or data.startswith("write_to_team_leaders") or data.startswith("write_to_tournament_judges"):
        return await handle_recipient_choice(update, context)

    # 16) если ничего не подошло
    await query.edit_message_text(f"Вы выбрали опцию: {data}")
    return ConversationHandler.END
