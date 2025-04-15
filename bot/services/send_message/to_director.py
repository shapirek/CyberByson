def send_message_to_director(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Получаем список ID дирекции (статус '0'), исключая отправителя
    receivers = [user['id'] for user in users_data
                 if user.get('статус') == '0' and user.get('id') and user['id'] != sender['id']]

    if not receivers:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Нет сотрудников в дирекции!")
        else:
            update.message.reply_text("❌ Нет сотрудников в дирекции!")
    else:
        for user_id in receivers:
            try:
                send_message_with_signature(
                    context, user_id, message_text, sender['имя'], sender['фамилия'], sender['статус'], recipient_type='director'
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Отправляем подтверждение об успешной отправке
        if update.callback_query:
            update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            update.message.reply_text("✅ Сообщения отправлены!")
