def handle_team_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith('team_'):
        team = data.split('_')[1]
        context.user_data['selected_team'] = team
        context.user_data['recipient_type'] = 'team'  # Добавляем тип получателя
        query.edit_message_text(text=f"Введите сообщение для команды {team}:")
        return INPUT_MESSAGE
    elif data == 'back_to_message_options':
        return show_message_options(update, context)
    else:
        query.edit_message_text("❌ Неизвестная команда.")
        return ConversationHandler.END
