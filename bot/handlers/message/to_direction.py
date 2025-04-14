def handle_direction_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'back_to_director':  # Обработка кнопки "Назад"
        # Получаем текущего пользователя
        sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
        if not sender:
            query.edit_message_text("❌ Ошибка: отправитель не найден!")
            return ConversationHandler.END

        # Возвращаем в меню дирекции или сотрудников
        if sender['статус'] == '0':  # Дирекция
            return show_director_menu(update, context)
        else:  # Сотрудник
            return show_staff_menu(update, context)
    else:
        context.user_data['selected_direction'] = data
        context.user_data['recipient_type'] = 'direction'  # Тип получателя
        query.edit_message_text(text="Введите послание:")
        return INPUT_MESSAGE
