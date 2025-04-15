async def show_staff_menu(update: Update, context: CallbackContext) -> int:
    # Проверяем, есть ли сообщение в update
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id

    keyboard = [
        [InlineKeyboardButton("НОВОСТИ", callback_data='news')],
        [InlineKeyboardButton("Запросить технику", callback_data='request_equipment')],
        [InlineKeyboardButton("Выдать наряд", callback_data='assign_duty')],
        [InlineKeyboardButton("Написать сообщение...", callback_data='staff_write_message')],
        [InlineKeyboardButton("Написать слона/педаль", callback_data='staff_write_something')],
        [InlineKeyboardButton("Турниры", callback_data='staff_tournaments')],
        [InlineKeyboardButton("Дежурство", callback_data='nadzor')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с клавиатурой
    await context.bot.send_message(chat_id=chat_id, text="Меню сотрудников:", reply_markup=reply_markup)
    return STAFF_ACTION
