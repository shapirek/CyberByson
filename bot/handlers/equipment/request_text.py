def handle_equipment_input(update: Update, context: CallbackContext) -> int:
    # Сохраняем текст сообщения в context.user_data
    equipment_request = update.message.text
    context.user_data['equipment_request'] = equipment_request

    # Получаем отправителя
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Отправляем запрос на технику в канал
    send_plea_to_channel(context, equipment_request, sender['имя'], sender['фамилия'], sender['статус'], recipient_type='equipment_request')

    # Получаем ID сообщения и thread_id из context.user_data
    unique_id = context.user_data.get('current_message_id')
    message_data = context.user_data.get(unique_id, {})
    channel_message_id = message_data.get('channel_message_id')
    thread_id = message_data.get('thread_id')

    if not channel_message_id or not thread_id:
        update.message.reply_text("❌ Ошибка: не удалось получить ID сообщения или треда.")
        return ConversationHandler.END

    # Формируем ссылку на тред
    thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{channel_message_id}?thread={thread_id}"

    print(f"[DEBUG] Ссылка на тред: {thread_url}")  # Отладочный вывод

    # Получаем список технозондеров (у которых в 9-ой колонке стоит 1)
    tech_zonders = [user['id'] for user in users_data if user.get('технозондер') == '1']

    if not tech_zonders:
        update.message.reply_text("❌ Нет технозондеров для рассылки!")
    else:
        # Формируем сообщение с подписью
        formatted_message = (
            f"📢 ЗАПРОС ТЕХНИКИ 📢\n\n"
            f"{equipment_request}\n\n"
            f"С уважением,\n"
            f"{sender['имя']} {sender['фамилия']}"
        )

        # Создаем клавиатуру с кнопкой "Подставить техноплечо"
        keyboard = [
            [InlineKeyboardButton("Подставить техноплечо 🦾", url=thread_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем сообщение всем технозондерам
        for user_id in tech_zonders:
            try:
                context.bot.send_message(
                    chat_id=user_id,
                    text=formatted_message,
                    reply_markup=reply_markup
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Уведомляем отправителя об успешной отправке
        update.message.reply_text("✅ Запрос на технику отправлен всем технозондерам!")

    # Возвращаемся в главное меню
    return show_staff_menu(update, context)
