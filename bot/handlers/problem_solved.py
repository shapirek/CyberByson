def handle_problem_solved_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    print(f"[DEBUG] Callback data: {query.data}")  # Проверьте вывод в консоли

    # Извлекаем unique_id из callback_data
    if not query.data.startswith('problem_solved_'):
        return

    unique_id = query.data.split('_')[2]  # Формат: 'problem_solved_{unique_id}'
    handle_problem_solved(update, context, unique_id)

def handle_problem_solved(update: Update, context: CallbackContext, unique_id: str) -> None:
    """
    Обрабатывает нажатие кнопки "Проблема решена!" и удаляет сообщения из канала, группы и открепляет сообщение.
    """
    query = update.callback_query
    query.answer()

    # Получаем данные для этого сообщения
    message_data = context.user_data.get(unique_id, {})
    if not message_data:
        query.edit_message_text("❌ Ошибка: данные сообщения не найдены.")
        return

    # Удаляем сообщение из канала
    if 'channel_message_id' in message_data:
        try:
            context.bot.delete_message(chat_id=CHANNEL_ID, message_id=message_data['channel_message_id'])
        except Exception as e:
            print(f"Ошибка удаления сообщения из канала: {e}")

    # Удаляем сообщение из группы
    if 'group_message_id' in message_data:
        try:
            context.bot.delete_message(chat_id=GROUP_ID, message_id=message_data['group_message_id'])
        except Exception as e:
            print(f"Ошибка удаления сообщения из группы: {e}")

    # Открепляем сообщение в диалоге с ботом
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if sender and 'group_message_id' in message_data:
        try:
            context.bot.unpin_chat_message(chat_id=sender['id'], message_id=message_data['group_message_id'])
            print(f"[DEBUG] Сообщение {message_data['group_message_id']} откреплено.")  # Отладочный вывод
        except Exception as e:
            print(f"Ошибка открепления сообщения: {e}")

    # Редактируем сообщение с кнопками, чтобы отобразить текст "Проблема решена"
    try:
        query.edit_message_text("✅ Проблема отмечена как решенная. Сообщения удалены и откреплены.")
    except Exception as e:
        print(f"Ошибка редактирования сообщения: {e}")

    # Удаляем данные для этого сообщения
    context.user_data.pop(unique_id, None)
