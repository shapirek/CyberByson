def send_message_with_button(update: Update, context: CallbackContext, recipient_type: str, **kwargs) -> None:
    message_text = context.user_data.get('message_text')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return

    # Отправляем сообщение в канал и получаем его ID и thread_id
    send_message_to_channel(context, message_text, sender['имя'], sender['фамилия'], sender['статус'], recipient_type, **kwargs)
    message_id = context.user_data.get('channel_message_id')
    thread_id = context.user_data.get('thread_id')
    thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{message_id}?thread={thread_id}"

    # Формируем сообщение с подписью и тегами
    formatted_message = format_message_with_signature(
        message_text, sender['имя'], sender['фамилия'], sender['статус'], recipient_type, **kwargs
    )

    # Добавляем кнопку "Подставить плечо" с ссылкой на тред
    keyboard = [[InlineKeyboardButton("Подставить плечо 💪", url=thread_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Определяем получателей, исключая отправителя
    if recipient_type == 'direction':
        receivers = [user['id'] for user in users_data
                     if user.get('направление') == kwargs.get('direction') and user['id'] != sender['id']]
    elif recipient_type == 'team':
        receivers = [user['id'] for user in users_data
                     if user.get('команда') == kwargs.get('team') and user['id'] != sender['id']]
    elif recipient_type == 'director':
        receivers = [user['id'] for user in users_data
                     if user.get('статус') == '0' and user['id'] != sender['id']]
    elif recipient_type == 'all_staff':
        receivers = [user['id'] for user in users_data
                     if user.get('id') and user['id'] != sender['id']]
    elif recipient_type == 'tournament_judges':
        receivers = [
            user['id'] for user in users_data
            if user.get('судья') == '1' and user.get('направление') in kwargs.get('directions', [])
            and user['id'] != sender['id']
        ]
    else:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: тип получателя не определен!")
        else:
            update.message.reply_text("❌ Ошибка: тип получателя не определен!")
        return

    # Отправляем сообщение получателям
    for user_id in receivers:
        try:
            context.bot.send_message(chat_id=user_id, text=formatted_message, reply_markup=reply_markup)
        except Exception as e:
            print(f"Ошибка отправки сообщения {user_id}: {e}")

    # Отправляем копию сообщения отправителю
    send_copy_to_sender(update, context, message_text)
