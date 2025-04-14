def director_announcement(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    return show_message_options(update, context)
