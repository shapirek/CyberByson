# Функция обработки команды /start. Отправляем приветственное сообщение и показываем главное меню.
def start(update: Update, context: CallbackContext) -> int:
    # Сбрасываем все данные пользователя
    context.user_data.clear()

    # Отправляем приветственное сообщение и показываем главное меню
    update.message.reply_text("Вас приветствует КиберБизон!\n Этот бот предназначен помочь упростить некоторые процессы в КЛШ.\n Если что-то пошло не так, рекомендуем "перезагрузить" бота — написать команду /start.")
    show_main_menu(update, context)

    return ConversationHandler.END  # Сбрасываем состояние

# Главное меню – используется клавиатура первого типа (ReplyKeyboardMarkup)
def show_main_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ['Школьники', 'Сотрудники'],
        ['Родители'],
        ['Завершить диалог']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)

# Альтернативная функция для вызова главного меню из callback‑обработчика (так как update.message может отсутствовать)
def show_main_menu_in_chat(context: CallbackContext, chat_id: int) -> None:
    keyboard = [
        ['Школьники', 'Сотрудники'],
        ['Родители'],
        ['Завершить диалог']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=chat_id, text="Выберите категорию:", reply_markup=reply_markup)
