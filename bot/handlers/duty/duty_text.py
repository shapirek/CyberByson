def handle_duty_text_input(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает ввод текста наряда и отправляет его.
    """
    duty_text = update.message.text.strip()  # Получаем текст наряда

    # Загружаем данные из таблицы TABULA
    try:
        users_data = read_google_sheet(TABULA)
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    # Получаем отправителя
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Получаем данные школьника из context
    selected_student = context.user_data.get('selected_student')
    if not selected_student:
        update.message.reply_text("❌ Ошибка: данные школьника не найдены.")
        return ConversationHandler.END

    # Формируем сообщение с нарядом
    message_text = (
        f"🚨 НАРЯД 🚨\n\n"
        f"КОМУ: {selected_student['имя']} {selected_student['фамилия']} ({selected_student['команда']})\n"
        f"ОТ КОГО: {sender['имя']} {sender['фамилия']} ({sender['команда']})\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{duty_text}"
    )

    # Получаем список пользователей, у которых в 10-й колонке стоит 1
    recipients = [user for user in users_data if user.get('псин') == '1']

    if not recipients:
        update.message.reply_text("❌ Нет назначенных сотрудников ПСИН.")
        return ConversationHandler.END

    # Отправляем сообщение каждому получателю
    for recipient in recipients:
        try:
            context.bot.send_message(
                chat_id=recipient['id'],
                text=message_text
            )
        except Exception as e:
            print(f"Ошибка отправки сообщения {recipient['id']}: {e}")

    # Уведомляем отправителя об успешной отправке
    update.message.reply_text("✅ Запрос отправлен всем сотрудникам ПСИН!")

    # Возвращаемся в главное меню
    return show_staff_menu(update, context)
