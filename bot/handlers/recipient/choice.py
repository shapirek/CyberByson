def handle_recipient_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'back_to_previous_menu':
        sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
        if not sender:
            query.edit_message_text("❌ Ошибка: отправитель не найден!")
            return ConversationHandler.END

        if sender['статус'] == '0':
            return show_director_menu(update, context)
        else:
            return show_staff_menu(update, context)
    elif data == 'write_to_department':
        return show_directions_menu(update, context)
    elif data == 'write_to_team_leaders':
        return show_team_leaders_menu(update, context)
    elif data == 'write_to_tournament_judges':
        return show_tournament_judges_menu(update, context)
    elif data == 'write_to_director':
        context.user_data['recipient_type'] = 'director'
        query.edit_message_text(text="Введите послание:")
        return INPUT_MESSAGE
    elif data == 'write_to_all_staff':
        context.user_data['recipient_type'] = 'all_staff'
        query.edit_message_text(text="Введите послание:")
        return INPUT_MESSAGE
    else:
        context.user_data['recipient'] = data
        query.edit_message_text(text="Введите послание:")
        return INPUT_MESSAGE

def handle_wait_for_response(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data

    # Получаем текст сообщения из context.user_data
    message_text = context.user_data.get('message_text')
    recipient_type = context.user_data.get('recipient_type')

    # Получаем отправителя
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        query.edit_message_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    if data == 'wait_for_response_no':
        # Если выбран вариант "Нет", отправляем сообщение как обычно
        if recipient_type == 'direction':
            send_message_to_direction(update, context)
        elif recipient_type == 'team':
            send_message_to_team(update, context)
        elif recipient_type == 'director':
            send_message_to_director(update, context)
        elif recipient_type == 'all_staff':
            send_message_to_all_staff(update, context)
        elif recipient_type == 'tournament_judges':
            send_message_to_tournament_judges(update, context)
        else:
            query.edit_message_text("❌ Ошибка: тип получателя не определен!")
            return ConversationHandler.END

        # Отправляем копию отправителю без кнопок
        send_plain_copy_to_sender(update, context, message_text)

        # Возвращаем в меню
        if sender['статус'] == '0':  # Если отправитель — дирекция
            return show_director_menu(update, context)
        else:  # Если отправитель — сотрудник
            return show_staff_menu(update, context)

    elif data == 'wait_for_response_yes':
        # Если выбран вариант "Да", отправляем сообщение с кнопкой, копию отправителю и в канал
        if recipient_type == 'direction':
            send_message_with_button(update, context, recipient_type, direction=context.user_data.get('selected_direction'))
        elif recipient_type == 'team':
            send_message_with_button(update, context, recipient_type, team=context.user_data.get('selected_team'))
        elif recipient_type == 'director':
            send_message_with_button(update, context, recipient_type)
        elif recipient_type == 'all_staff':
            send_message_with_button(update, context, recipient_type)
        elif recipient_type == 'tournament_judges':
            send_message_with_button(update, context, recipient_type, tournament=context.user_data.get('selected_tournament'))
        else:
            query.edit_message_text("❌ Ошибка: тип получателя не определен!")
            return ConversationHandler.END

        # Возвращаем в меню
        if sender['статус'] == '0':  # Если отправитель — дирекция
            return show_director_menu(update, context)
        else:  # Если отправитель — сотрудник
            return show_staff_menu(update, context)
    else:
        query.edit_message_text("❌ Неизвестная команда.")
        return ConversationHandler.END
