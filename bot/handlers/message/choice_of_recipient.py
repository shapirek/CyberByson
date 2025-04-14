from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import asyncio  # Для асинхронной версии
from functools import partial  # Для частичного применения функций


async def handle_recipient_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    # Кэширование данных пользователей
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()

    users_data = context.bot_data['users_data']

    if data == 'back_to_previous_menu':
        sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
        if not sender:
            await query.edit_message_text("❌ Ошибка: отправитель не найден!")
            return ConversationHandler.END

        return await (show_director_menu if sender['статус'] == '0' else show_staff_menu)(update, context)

    # Оптимизация через словарь обработчиков
    handlers = {
        'write_to_department': show_directions_menu,
        'write_to_team_leaders': show_team_leaders_menu,
        'write_to_tournament_judges': show_tournament_judges_menu,
        'write_to_director': partial(set_recipient_and_prompt, 'director'),
        'write_to_all_staff': partial(set_recipient_and_prompt, 'all_staff')
    }

    if data in handlers:
        return await handlers[data](update, context)
    
    # Обработка произвольного получателя
    context.user_data['recipient'] = data
    await query.edit_message_text(text="Введите послание:")
    return INPUT_MESSAGE

async def set_recipient_and_prompt(recipient_type: str, update: Update, context: CallbackContext) -> int:
    context.user_data['recipient_type'] = recipient_type
    await update.callback_query.edit_message_text(text="Введите послание:")
    return INPUT_MESSAGE

async def handle_wait_for_response(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    # Проверка данных
    if not all(key in context.user_data for key in ['message_text', 'recipient_type']):
        await query.edit_message_text("❌ Ошибка: недостаточно данных!")
        return ConversationHandler.END

    # Кэширование данных пользователей
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()

    users_data = context.bot_data['users_data']
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        await query.edit_message_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Оптимизация через словарь обработчиков
    response_handlers = {
        'wait_for_response_no': handle_no_response,
        'wait_for_response_yes': handle_yes_response
    }

    if data in response_handlers:
        return await response_handlers[data](update, context, sender)
    
    await query.edit_message_text("❌ Неизвестная команда.")
    return ConversationHandler.END

async def handle_no_response(update: Update, context: CallbackContext, sender: dict) -> int:
    recipient_type = context.user_data['recipient_type']
    message_text = context.user_data['message_text']

    # Словарь обработчиков отправки
    send_handlers = {
        'direction': send_message_to_direction,
        'team': send_message_to_team,
        'director': send_message_to_director,
        'all_staff': send_message_to_all_staff,
        'tournament_judges': send_message_to_tournament_judges
    }

    if recipient_type not in send_handlers:
        await update.callback_query.edit_message_text("❌ Ошибка: тип получателя не определен!")
        return ConversationHandler.END

    await send_handlers[recipient_type](update, context)
    await send_plain_copy_to_sender(update, context, message_text)

    return await (show_director_menu if sender['статус'] == '0' else show_staff_menu)(update, context)

async def handle_yes_response(update: Update, context: CallbackContext, sender: dict) -> int:
    recipient_type = context.user_data['recipient_type']
    extra_data = {
        'direction': context.user_data.get('selected_direction'),
        'team': context.user_data.get('selected_team'),
        'tournament': context.user_data.get('selected_tournament')
    }.get(recipient_type)

    await send_message_with_button(update, context, recipient_type, extra_data)
    return await (show_director_menu if sender['статус'] == '0' else show_staff_menu)(update, context)
