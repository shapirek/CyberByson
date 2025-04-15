def send_plea_to_channel(context: CallbackContext, message_text: str, sender_name: str, sender_surname: str,
                          sender_status: str, recipient_type: str, **kwargs) -> None:
    """
    Отправляет копию сообщения в канал и сохраняет ID сообщения и thread_id.
    """
    formatted_message = format_message_with_signature(
        message_text, sender_name, sender_surname, sender_status, recipient_type, **kwargs
    )

    try:
        # Отправляем сообщение в канал
        sent_message = context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=formatted_message,  # Отправляем текст как есть, без Markdown-разметки
        )

        # Сохраняем ID сообщения и thread_id
        unique_id = generate_unique_id()
        message_data = {
            'channel_message_id': sent_message.message_id,
            'thread_id': sent_message.message_id,  # Используем message_id как thread_id
        }
        context.user_data[unique_id] = message_data

        # Сохраняем уникальный идентификатор в context.user_data
        context.user_data['current_message_id'] = unique_id

    except Exception as e:
        print(f"Ошибка отправки сообщения в канал: {e}")
