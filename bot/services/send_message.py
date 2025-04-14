def send_message_to_channel(context: CallbackContext, message_text: str, sender_name: str, sender_surname: str,
                          sender_status: str, recipient_type: str, **kwargs) -> None:
    """
    Отправляет копию сообщения в канал и сохраняет ID сообщения и thread_id.
    """
    formatted_message = format_message_with_signature(
        message_text, sender_name, sender_surname, sender_status, recipient_type, **kwargs
    )

    try:
        # Проверяем, есть ли thread_id
        thread_id = context.user_data.get('thread_id')
        reply_to_message_id = thread_id if thread_id else None

        # Отправляем сообщение в канал
        sent_message = context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=formatted_message,  # Отправляем текст как есть, без Markdown-разметки
            reply_to_message_id=reply_to_message_id  # Указываем thread_id, если он есть
        )

        # Генерируем уникальный идентификатор для этого сообщения
        unique_id = generate_unique_id()

        # Сохраняем данные для этого сообщения
        message_data = {
            'channel_message_id': sent_message.message_id,
            'thread_id': sent_message.message_id,  # Сохраняем thread_id
            'group_message_id': None  # Будет заполнено позже
        }
        context.user_data[unique_id] = message_data

        # Сохраняем уникальный идентификатор в context.user_data
        context.user_data['current_message_id'] = unique_id

    except Exception as e:
        print(f"Ошибка отправки сообщения в канал: {e}")

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

def send_message_to_all_staff(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Получаем список ID всех сотрудников, исключая отправителя
    receivers = [user['id'] for user in users_data
                 if user.get('id') and user['id'] != sender['id']]

    if not receivers:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Нет сотрудников для рассылки!")
        else:
            update.message.reply_text("❌ Нет сотрудников для рассылки!")
    else:
        for user_id in receivers:
            try:
                send_message_with_signature(
                    context, user_id, message_text, sender['имя'], sender['фамилия'], sender['статус'], recipient_type='all_staff'
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Отправляем подтверждение об успешной отправке
        if update.callback_query:
            update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            update.message.reply_text("✅ Сообщения отправлены!")

def send_message_to_direction(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    direction = context.user_data.get('selected_direction')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Получаем список ID для рассылки, исключая отправителя
    receivers = [user['id'] for user in users_data
                 if user.get('направление') == direction and user['id'] != sender['id']]

    if not receivers:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Нет сотрудников в этом направлении!")
        else:
            update.message.reply_text("❌ Нет сотрудников в этом направлении!")
    else:
        for user_id in receivers:
            try:
                send_message_with_signature(
                    context, user_id, message_text, sender['имя'], sender['фамилия'], sender['статус'], direction
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Отправляем подтверждение об успешной отправке
        if update.callback_query:
            update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            update.message.reply_text("✅ Сообщения отправлены!")

def send_message_to_team(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    team = context.user_data.get('selected_team')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Получаем список ID для рассылки, исключая отправителя
    receivers = [user['id'] for user in users_data
                 if user.get('команда') == team and user['id'] != sender['id']]

    if not receivers:
        if update.callback_query:
            update.callback_query.edit_message_text(f"❌ Нет вожатых в команде {team}!")
        else:
            update.message.reply_text(f"❌ Нет вожатых в команде {team}!")
    else:
        for user_id in receivers:
            try:
                send_message_with_signature(
                    context, user_id, message_text, sender['имя'], sender['фамилия'], sender['статус'], team=team
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Отправляем подтверждение об успешной отправке
        if update.callback_query:
            update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            update.message.reply_text("✅ Сообщения отправлены!")

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
