# Функция обработки команды /start. Отправляем приветственное сообщение и показываем главное меню.
def start(update: Update, context: CallbackContext) -> int:
    # Сбрасываем все данные пользователя
    context.user_data.clear()

    # Отправляем приветственное сообщение и показываем главное меню
    update.message.reply_text("Вас приветствует КиберБизон!\n Этот бот предназначен помочь упростить некоторые процессы в КЛШ.\n Если что-то пошло не так, рекомендуем "перезагрузить" бота — написать команду /start.")
    show_main_menu(update, context)

    return ConversationHandler.END  # Сбрасываем состояние

def handle_category(update: Update, context: CallbackContext) -> int:
    category = update.message.text
    if category == 'Завершить диалог':
        update.message.reply_text("Диалог завершён. До новых встреч!")
        return ConversationHandler.END
    elif category == 'Родители':
        return show_parents_menu(update, context)  # Возвращаем состояние PARENTS_ACTION
    elif category == 'Школьники':
        return show_students_menu(update, context)  # Возвращаем состояние STUDENTS_ACTION
    elif category == 'Сотрудники':
        try:
            # Загружаем таблицу при выборе "Сотрудники"
            global users_data
            users_data = read_google_sheet(TABULA)
            print("Данные успешно загружены!")
            update.message.reply_text("Укажите Ваш код доступа:")
            return CODE_INPUT  # Переходим в состояние ввода кода
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
            return ConversationHandler.END
    return ConversationHandler.END
