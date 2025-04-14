def handle_child_name_input(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    parts = user_input.split()

    if len(parts) < 2:
        update.message.reply_text("❌ Пожалуйста, введите имя и фамилию ребенка.")
        return INPUT_CHILD_NAME

    # Используем сохраненные данные из контекста
    kids_data = context.user_data.get('kids_data')
    if not kids_data:
        update.message.reply_text("⚠️ Ошибка: данные школьников не загружены.")
        return ConversationHandler.END

    # Поиск ребенка (аналогично предыдущей логике)
    search_list = [f"{kid['фамилия']} {kid['имя']}" for kid in kids_data]
    matches = process.extract(user_input, search_list, limit=5)
    filtered_matches = [match for match, score in matches if score >= 70]

    if not filtered_matches:
        update.message.reply_text("❌ Не удалось найти ребенка. Попробуйте еще раз.")
        return INPUT_CHILD_NAME

    matched_children = [
        kid for kid in kids_data
        if f"{kid['фамилия']} {kid['имя']}" in filtered_matches
    ]

    # Если найдено только одно совпадение, сразу переходим к вводу сообщения
    if len(matched_children) == 1:
        context.user_data['selected_child'] = matched_children[0]
        update.message.reply_text(
            f"✅ Вы выбрали:\n\n"
            f"{matched_children[0]['имя']} {matched_children[0]['фамилия']} ({matched_children[0]['команда']})"
        )
        # Отправляем отдельное сообщение с запросом на ввод текста наряда
        update.message.reply_text("Это сообщение будет направлено вожатым. Напишие, что нужно передать:")
        return INPUT_MESSAGE_FOR_CHILD

    # Если найдено несколько совпадений, предлагаем выбрать
    keyboard = [
        [InlineKeyboardButton(
            f"{child['фамилия']} {child['имя']} {child['отчество']} ({child['команда']})",
            callback_data=f"select_child_{idx}"
        )]
        for idx, child in enumerate(matched_children)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Найдено несколько детей. Выберите нужного:",
        reply_markup=reply_markup
    )

    # Сохраняем список совпадений в context
    context.user_data['matched_children'] = matched_children

    return CHOOSE_CHILD
