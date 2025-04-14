from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


async def handle_direction_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'back_to_director':
        # Кэширование данных пользователей
        if 'users_data' not in context.bot_data:
            context.bot_data['users_data'] = await load_users_data_async()
        
        sender = next((u for u in context.bot_data['users_data'] 
                      if str(u['код']) == context.user_data.get('code')), None)
        
        if not sender:
            await query.edit_message_text("❌ Ошибка: отправитель не найден!")
            return ConversationHandler.END

        # Используем тернарный оператор для выбора меню
        menu_func = show_director_menu if sender['статус'] == '0' else show_staff_menu
        return await menu_func(update, context)
    
    # Оптимизированное сохранение данных
    context.user_data.update({
        'selected_direction': data,
        'recipient_type': 'direction'
    })
    
    await query.edit_message_text(text="Введите послание:")
    return INPUT_MESSAGE
