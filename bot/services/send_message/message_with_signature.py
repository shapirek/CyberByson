def send_message_with_signature(context: CallbackContext, chat_id: str, message_text: str, sender_name: str, sender_surname: str, sender_status: str, recipient_type: str = None, **kwargs) -> None:
    """
    Отправляет сообщение с подписью и, если нужно, с кнопкой "Подставить плечо".
    """
    # Формируем сообщение с подписью
    formatted_message = format_message_with_signature(
        message_text, sender_name, sender_surname, sender_status, recipient_type, **kwargs
    )

    # Отправляем сообщение
    context.bot.send_message(chat_id=chat_id, text=formatted_message, parse_mode='Markdown')
