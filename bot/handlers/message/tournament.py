def handle_tournament_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith('tournament_'):
        tournament = data.split('_')[1]
        context.user_data['selected_tournament'] = tournament  # Сохраняем выбранный турнир
        context.user_data['recipient_type'] = 'tournament_judges'  # Тип получателя — судьи турнира
        query.edit_message_text(text=f"Введите сообщение для судей {tournament}:")
        return INPUT_MESSAGE
    elif data == 'back_to_message_options':
        return show_message_options(update, context)
    else:
        query.edit_message_text("❌ Неизвестный турнир.")
        return ConversationHandler.END
