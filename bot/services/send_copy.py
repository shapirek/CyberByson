def send_copy_to_sender(update: Update, context: CallbackContext, message_text: str) -> None:
    """
    Отправляет копию сообщения отправителю с кнопками-ссылками и закрепляет его в диалоге.
    """
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        return

    # Получаем уникальный идентификатор текущего сообщения
    unique_id = context.user_data.get('current_message_id')
    if not unique_id:
        return

    # Получаем данные для текущего сообщения
    message_data = context.user_data.get(unique_id, {})
    channel_message_id = message_data.get('channel_message_id')
    thread_id = message_data.get('thread_id')
    thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{channel_message_id}?thread={thread_id}"

    # Формируем сообщение с подписью и тегами
    formatted_message = (
        f"📨 КОПИЯ СООБЩЕНИЯ 📨\n {generate_tags(message_text)}\n\n"
        f"{message_text}\n\n"
        f"С уважением,\n"
        f"{sender['имя']} {sender['фамилия']}"
    )

    # Создаем клавиатуру с кнопками-ссылками
    keyboard = [
        [
            InlineKeyboardButton("Ответы", url=thread_url),
            InlineKeyboardButton("Проблема решена!", callback_data=f'problem_solved_{unique_id}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Отправляем сообщение отправителю
        sent_message = context.bot.send_message(
            chat_id=sender['id'],
            text=formatted_message,
            reply_markup=reply_markup
        )

        # Закрепляем сообщение в диалоге
        context.bot.pin_chat_message(chat_id=sender['id'], message_id=sent_message.message_id)

        # Сохраняем ID сообщения в данных текущего сообщения
        message_data['group_message_id'] = sent_message.message_id
        context.user_data[unique_id] = message_data

    except Exception as e:
        print(f"Ошибка отправки сообщения отправителю: {e}")

def send_plain_copy_to_sender(update: Update, context: CallbackContext, message_text: str) -> None:
    """
    Отправляет копию сообщения отправителю без кнопок, с тегами.
    """
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        return  # Если отправитель не найден, ничего не делаем

    # Формируем текст сообщения для отправителя с тегами
    formatted_message = (
        f"📨 КОПИЯ СООБЩЕНИЯ 📨\n {generate_tags(message_text)}\n\n"
        f"{message_text}\n\n"
        f"С уважением,\n"
        f"{sender['имя']} {sender['фамилия']}"
    )

    # Отправляем сообщение отправителю без кнопок
    try:
        context.bot.send_message(chat_id=sender['id'], text=formatted_message)
    except Exception as e:
        print(f"Ошибка отправки сообщения отправителю: {e}")
