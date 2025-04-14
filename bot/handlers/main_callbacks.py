from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import logging
from functools import partial


# Обработка нажатий на inline‑кнопки.
logger = logging.getLogger(__name__)

async def inline_button_handler(update: Update, context: CallbackContext) -> int:
    """Асинхронный обработчик inline-кнопок с оптимизированной логикой."""
    query = update.callback_query
    await query.answer()

    # Игнорируем problem_solved_* события
    if query.data.startswith('problem_solved_'):
        return ConversationHandler.END

    # Словарь обработчиков для кнопок
    handlers = {
        'back_to_main': handle_back_to_main,
        'news': handle_news_async,
        'assign_duty': handle_assign_duty_async,
        'back_to_director': show_director_menu_async,
        'back_to_staff': show_staff_menu_async,
        'back_to_parents': show_parents_menu_async,
        'back_to_students': show_students_menu_async,
        'director_write_department': show_directions_menu_async,
        'director_announcement': director_announcement_async,
        'staff_write_message': staff_write_message_async,
        'request_equipment': handle_request_equipment_async,
        'back_to_previous_menu': handle_back_to_previous_menu_async,
        'wait_for_response_yes': partial(handle_wait_for_response_async, response='yes'),
        'wait_for_response_no': partial(handle_wait_for_response_async, response='no'),
        'problem_solved': handle_problem_solved_async,
        'parent_call': handle_parent_call_async
    }

    # Выбор обработчика или обработка неизвестной команды
    handler = handlers.get(query.data, handle_unknown_command)
    try:
        return await handler(update, context)
    except Exception as e:
        logger.error(f"Ошибка обработки {query.data}: {str(e)}", exc_info=True)
        await query.edit_message_text("⚠️ Произошла внутренняя ошибка")
        return ConversationHandler.END

async def handle_back_to_previous_menu_async(update: Update, context: CallbackContext) -> int:
    """Асинхронный обработчик возврата в предыдущее меню."""
    query = update.callback_query
    
    # Кэширование данных пользователей
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    
    # Поиск пользователя
    sender = next(
        (u for u in context.bot_data['users_data'] 
         if str(u['код']) == context.user_data.get('code')),
        None
    )
    
    if not sender:
        await query.edit_message_text("❌ Ошибка: пользователь не найден!")
        return ConversationHandler.END

    # Словарь обработчиков меню
    menu_handlers = {
        '0': show_director_menu_async,
        '1': show_staff_menu_async,
        '2': show_parents_menu_async,
        '3': show_students_menu_async
    }
    
    return await menu_handlers.get(
        sender.get('статус', 'unknown'), 
        handle_unknown_status
    )(update, context)

async def handle_unknown_command(update: Update, context: CallbackContext) -> int:
    """Обработчик неизвестных команд."""
    query = update.callback_query
    await query.edit_message_text(f"❌ Неизвестная команда: {query.data}")
    return ConversationHandler.END

async def handle_unknown_status(update: Update, context: CallbackContext) -> int:
    """Обработчик неизвестного статуса."""
    query = update.callback_query
    await query.edit_message_text("⚠️ Неизвестный статус пользователя!")
    return ConversationHandler.END
