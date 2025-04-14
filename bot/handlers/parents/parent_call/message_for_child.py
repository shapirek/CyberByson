def handle_message_for_child_input(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает ввод сообщения для ребенка и отправляет его вожатым.
    """
    message_text = update.message.text.strip()  # Получаем текст сообщения

    # Получаем данные ребенка из context
    selected_child = context.user_data.get('selected_child')
    if not selected_child:
        update.message.reply_text("❌ Ошибка: данные ребенка не найдены.")
        return ConversationHandler.END

    # Загружаем данные из таблицы TABULA (сотрудники)
    try:
        staff_data = read_google_sheet(TABULA)
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    # Получаем команду выбранного ребенка
    child_team = selected_child.get('команда')

    if not child_team:
        update.message.reply_text("❌ Ошибка: не удалось определить команду ребенка.")
        return ConversationHandler.END

    # Находим сотрудников с совпадающей командой
    matched_staff = [staff for staff in staff_data if staff.get('команда') == child_team]

    if not matched_staff:
        update.message.reply_text("❌ Не найдено вожатых для команды ребенка.")
        return ConversationHandler.END

    # Формируем сообщение для вожатых
    message_for_staff = (
        f"🙏 РОДИТЕЛИ ПЕРЕДАЮТ 🙏\n\n"
        f"{selected_child['имя']} {selected_child['фамилия']}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{message_text}"
    )

    # Отправляем сообщение каждому вожатому
    for staff in matched_staff:
        try:
            context.bot.send_message(
                chat_id=staff['id'],  # ID сотрудника
                text=message_for_staff
            )
        except Exception as e:
            print(f"Ошибка отправки сообщения {staff['id']}: {e}")

    # Уведомляем отправителя об успешной отправке
    update.message.reply_text("✅ Сообщение отправлено вожатым команды!")

    # Возвращаемся в главное меню
    return show_parents_menu(update, context)
