def handle_student_info_input(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает ввод пользователя и ищет школьников по имени и фамилии.
    Если найдено несколько совпадений, предлагает выбрать школьника.
    """
    user_input = update.message.text.strip()  # Получаем ввод пользователя

    # Разделяем ввод на слова
    parts = user_input.split()
    if len(parts) < 2:
        update.message.reply_text("❌ Пожалуйста, введите имя и фамилию школьника.")
        return INPUT_STUDENT_INFO

    # Загружаем данные из второй вкладки
    try:
        parents_data = read_google_sheet_sheet2(TABULA_kids)
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    # Формируем список строк для поиска (Фамилия Имя)
    search_list = [
        f"{parent['фамилия']} {parent['имя']}" for parent in parents_data
    ]

    # Ищем ближайшие совпадения с порогом 70
    matches = process.extract(user_input, search_list, limit=5)  # Ограничиваем количество совпадений

    # Фильтруем совпадения с порогом 70
    filtered_matches = [match for match, score in matches if score >= 70]

    if not filtered_matches:
        update.message.reply_text("❌ Не удалось найти школьника. Попробуйте еще раз.")
        return INPUT_STUDENT_INFO

    # Находим данные для всех совпадений
    matched_parents = [
        parent for parent in parents_data
        if f"{parent['фамилия']} {parent['имя']}" in filtered_matches
    ]

    # Если найдено только одно совпадение, сразу переходим к вводу наряда
    if len(matched_parents) == 1:
        context.user_data['selected_student'] = matched_parents[0]
        update.message.reply_text(
            f"✅ Наряд получит:\n\n"
            f"{matched_parents[0]['фамилия']} {matched_parents[0]['имя']} ({matched_parents[0]['команда']})"
        )
        # Отправляем отдельное сообщение с запросом на ввод текста наряда
        update.message.reply_text("Укажите причину наряда:")
        return INPUT_DUTY_TEXT

    # Если найдено несколько совпадений, предлагаем выбрать
    keyboard = [
        [InlineKeyboardButton(
            f"{parent['фамилия']} {parent['имя']} {parent['отчество']} ({parent['команда']})",
            callback_data=f"select_student_{idx}"
        )]
        for idx, parent in enumerate(matched_parents)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Найдено несколько школьников. Выберите нужного:",
        reply_markup=reply_markup
    )

    # Сохраняем список совпадений в context
    context.user_data['matched_students'] = matched_parents

    return CHOOSE_STUDENT

def handle_student_choice(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает выбор школьника из списка.
    """
    query = update.callback_query
    query.answer()

    # Извлекаем индекс выбранного школьника
    selected_idx = int(query.data.split('_')[2])

    # Получаем список совпадений из context
    matched_students = context.user_data.get('matched_students')
    if not matched_students:
        query.edit_message_text("❌ Ошибка: данные школьников не найдены.")
        return ConversationHandler.END

    # Сохраняем выбранного школьника в context
    selected_student = matched_students[selected_idx]
    context.user_data['selected_student'] = selected_student

    # Уведомляем пользователя о выборе
    query.edit_message_text(
        f"✅ Наряд получит:\n\n"
        f"{selected_student['фамилия']} {selected_student['имя']} ({selected_student['команда']})\n"
    )

    # Отправляем отдельное сообщение с запросом на ввод текста наряда
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Укажите причину наряда:"
    )

    return INPUT_DUTY_TEXT
