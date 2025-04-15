async def show_parents_menu(update: Update, context: CallbackContext) -> int:
    # Загружаем данные из таблицы школьников (TABULA_kids)
    try:
        kids_data = await read_google_sheet_sheet2(TABULA_kids)  # Функция для Лист2
        context.user_data['kids_data'] = kids_data  # Сохраняем данные школьников
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        await update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    # Показываем меню для родителей
    keyboard = [
        [InlineKeyboardButton("Пусть ребенок мне позвонит!", callback_data='parent_call')],
        [InlineKeyboardButton("Что привезти ребенку?", callback_data='parent_gift')],
        [InlineKeyboardButton("Расписание КЛШ", callback_data='parent_schedule')],
        [InlineKeyboardButton("Телефоны дирекции", callback_data='parent_director_phones')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите опцию для родителей:", reply_markup=reply_markup)
    return PARENTS_ACTION
