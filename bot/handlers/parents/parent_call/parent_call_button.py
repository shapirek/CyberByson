def handle_parent_call(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает нажатие кнопки "Пусть ребенок мне позвонит!".
    Запрашивает имя ребенка.
    """
    query = update.callback_query
    query.answer()

    # Запрашиваем имя ребенка
    query.edit_message_text("Как зовут вашего ребенка?")

    return INPUT_CHILD_NAME
