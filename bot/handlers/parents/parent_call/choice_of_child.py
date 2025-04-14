def handle_child_choice(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает выбор ребенка из списка.
    """
    query = update.callback_query
    query.answer()

    # Извлекаем индекс выбранного ребенка
    selected_idx = int(query.data.split('_')[2])

    # Получаем список совпадений из context
    matched_children = context.user_data.get('matched_children')
    if not matched_children:
        query.edit_message_text("❌ Ошибка: данные детей не найдены.")
        return ConversationHandler.END

    # Сохраняем выбранного ребенка в context
    selected_child = matched_children[selected_idx]
    context.user_data['selected_child'] = selected_child

    # Уведомляем пользователя о выборе
    query.edit_message_text(
        f"✅ Вы выбрали:\n\n"
        f"{selected_child['имя']} {selected_child['фамилия']} ({selected_child['команда']})"
    )

    # Отправляем отдельное сообщение с запросом на ввод текста наряда
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Это сообщение будет направлено вожатым. Напишите, что нужно передать:"
    )
    return INPUT_MESSAGE_FOR_CHILD
