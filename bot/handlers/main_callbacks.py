# Обработка нажатий на inline‑кнопки.
def inline_button_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Пропускаем callback_data, которые начинаются с 'problem_solved_'
    if query.data.startswith('problem_solved_'):
        return ConversationHandler.END

    data = query.data

    if data == 'back_to_main':
        query.edit_message_text("Возвращаемся в главное меню.")
        show_main_menu_in_chat(context, query.message.chat_id)
        return ConversationHandler.END
    elif data == 'news':
        try:
            handle_news(update, context)
        except Exception as e:
            logger.error(f"News error: {str(e)}")
            query.edit_message_text("❌ Ошибка при загрузке новостей")
        return ConversationHandler.END
    elif data == 'assign_duty':
        return handle_assign_duty(update, context)  # Передаем query через update
    elif data == 'back_to_director':
        return show_director_menu(update, context)
    elif data == 'back_to_staff':
        return show_staff_menu(update, context)
    elif data == 'back_to_parents':
        return show_parents_menu(update, context)
    elif data == 'back_to_students':
        return show_students_menu(update, context)
    elif data == 'director_write_department':
        return show_directions_menu(update, context)
    elif data == 'director_announcement':
        return director_announcement(update, context)
    elif data == 'staff_write_message':
        return staff_write_message(update, context)
    elif data == 'request_equipment':  # Обработка кнопки "Запросить технику"
        return handle_request_equipment(update, context)
    elif data == 'assign_duty':  # Обработка кнопки "Выдать наряд"
        return handle_assign_duty(update, context)
    elif data == 'back_to_previous_menu':
        # Получаем текущего пользователя
        sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
        if not sender:
            query.edit_message_text("❌ Ошибка: отправитель не найден!")
            return ConversationHandler.END  # Завершаем диалог, если пользователь не найден

        # Возвращаем в меню соответствующей категории
        status = sender.get('статус')
        if status == '0':  # Дирекция
            return show_director_menu(update, context)
        elif status == '1':  # Сотрудник
            return show_staff_menu(update, context)
        elif status == '2':  # Родители
            return show_parents_menu(update, context)
        elif status == '3':  # Школьники
            return show_students_menu(update, context)
        else:
            query.edit_message_text("⚠️ Неизвестный статус пользователя!")
            return ConversationHandler.END  # Завершаем диалог, если статус неизвестен
    elif data in ['wait_for_response_yes', 'wait_for_response_no']:
        # Если данные относятся к новому функционалу, передаем их в handle_wait_for_response
        return handle_wait_for_response(update, context)
    elif data == 'problem_solved':
        # Обрабатываем нажатие кнопки "Проблема решена!"
        return handle_problem_solved(update, context)
    elif data == 'parent_call':  # Обработка кнопки "Пусть ребенок мне позвонит!"
        return handle_parent_call(update, context)
    else:
        query.edit_message_text(f"Вы выбрали опцию: {data}")
        return ConversationHandler.END  # Сбрасываем состояние после выполнения действия
