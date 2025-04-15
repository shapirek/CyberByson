def send_message_to_tournament_judges(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    tournament = context.user_data.get('selected_tournament')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Определяем направления для выбранного турнира
    if tournament == 'ФМТ':
        directions = ['НТН']
    elif tournament == 'ГУТ':
        directions = ['НФН', 'НОН']
    elif tournament == 'БХТ':
        directions = ['НЕН']
    else:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Неизвестный турнир!")
        else:
            update.message.reply_text("❌ Неизвестный турнир!")
        return ConversationHandler.END

    # Получаем список ID судей для выбранного турнира, исключая отправителя
    receivers = [
        user['id'] for user in users_data
        if user.get('судья') == '1' and user.get('направление') in directions
        and user.get('id') and user['id'] != sender['id']
    ]

    if not receivers:
        if update.callback_query:
            update.callback_query.edit_message_text(f"❌ Нет судей для {tournament}!")
        else:
            update.message.reply_text(f"❌ Нет судей для {tournament}!")
    else:
        for user_id in receivers:
            try:
                send_message_with_signature(
                    context, user_id, message_text, sender['имя'], sender['фамилия'], sender['статус'], recipient_type='tournament_judges', tournament=tournament
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Отправляем подтверждение об успешной отправке
        if update.callback_query:
            update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            update.message.reply_text("✅ Сообщения отправлены!")
