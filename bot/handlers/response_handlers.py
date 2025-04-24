import logging
import asyncio

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.common import load_users_data_async
from bot.services.send_messages.senders import send_message_with_button
from bot.services.send_messages.to_direction import send_message_to_direction
from bot.services.send_messages.to_team import send_message_to_team
from bot.services.send_messages.to_director import send_message_to_director
from bot.services.send_messages.to_all_staff import send_message_to_all_staff
from bot.services.send_messages.to_tournament_judges import send_message_to_tournament_judges
from bot.services.send_messages.copy_helpers import send_plain_copy_to_sender
from bot.utils.keyboards.director_menu import show_director_menu
from bot.utils.keyboards.staff_menu import show_staff_menu
from bot.config import INPUT_MESSAGE

logger = logging.getLogger(__name__)


async def handle_wait_for_response(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    После запроса “Хотите кнопку?”  
    - при “Нет” шлёт обычное сообщение + plain-копию  
    - при “Да” – вызывает send_message_with_button  
    и возвращает обратно в главное меню
    """
    query = update.callback_query
    await query.answer()
    choice = query.data

    # 1) Ensure users_data is loaded
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    users = context.bot_data['users_data']

    # 2) Gather context
    msg_text = context.user_data.get('message_text', '')
    recipient = context.user_data.get('recipient_type')
    code = str(context.user_data.get('code', ''))
    sender = next((u for u in users if str(u.get('код')) == code), None)
    if not sender:
        await query.edit_message_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # 3) Helper to pick next menu
    async def back_to_menu():
        if sender.get('статус') == '0':
            return await show_director_menu(update, context)
        return await show_staff_menu(update, context)

    # 4) Handle “Нет” (plain send)
    if choice == 'wait_for_response_no':
        # dispatch by recipient_type
        if recipient == 'direction':
            await send_message_to_direction(update, context)
        elif recipient == 'team':
            await send_message_to_team(update, context)
        elif recipient == 'director':
            await send_message_to_director(update, context)
        elif recipient == 'all_staff':
            await send_message_to_all_staff(update, context)
        elif recipient == 'tournament_judges':
            await send_message_to_tournament_judges(update, context)
        else:
            await query.edit_message_text("❌ Ошибка: тип получателя не определён!")
            return ConversationHandler.END

        # send plain copy
        await send_plain_copy_to_sender(update, context, msg_text)
        return await back_to_menu()

    # 5) Handle “Да” (with button)
    if choice == 'wait_for_response_yes':
        params = {}
        if recipient == 'direction':
            params['direction'] = context.user_data.get('selected_direction')
        elif recipient == 'team':
            params['team'] = context.user_data.get('selected_team')
        elif recipient == 'tournament_judges':
            params['tournament'] = context.user_data.get('selected_tournament')
        # director and all_staff need no extra params

        await send_message_with_button(update, context, recipient, **params)
        return await back_to_menu()

    # 6) Unknown
    await query.edit_message_text("❌ Неизвестная команда.")
    return ConversationHandler.END
