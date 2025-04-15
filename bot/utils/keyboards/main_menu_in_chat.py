async def show_main_menu_in_chat(context: CallbackContext, chat_id: int) -> None:
    keyboard = [
        ['Школьники', 'Сотрудники'],
        ['Родители'],
        ['Завершить диалог']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await context.bot.send_message(chat_id=chat_id, text="Выберите категорию:", reply_markup=reply_markup)
