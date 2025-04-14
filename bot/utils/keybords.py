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

# Inline‑меню для родителей
def show_parents_menu(update: Update, context: CallbackContext) -> int:
    # Загружаем данные из таблицы школьников (TABULA_kids)
    try:
        kids_data = read_google_sheet_sheet2(TABULA_kids)  # Функция для Лист2
        context.user_data['kids_data'] = kids_data  # Сохраняем данные школьников
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
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
    update.message.reply_text("Выберите опцию для родителей:", reply_markup=reply_markup)
    return PARENTS_ACTION

# Inline‑меню для школьников
def show_students_menu(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Что такое КЛШ?", callback_data='student_info')],
        [InlineKeyboardButton("Как попасть в КЛШ?", callback_data='student_how_to')],
        [InlineKeyboardButton("Буклет этого года", callback_data='student_booklet')],
        [InlineKeyboardButton("Архив КЛШ", callback_data='student_archive')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите опцию для школьников:", reply_markup=reply_markup)
    return STUDENTS_ACTION  # Возвращаем состояние меню школьников

def show_director_menu(update: Update, context: CallbackContext) -> int:
    # Проверяем, есть ли сообщение в update
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id

    keyboard = [
        [InlineKeyboardButton("НОВОСТИ", callback_data='news')],
        [InlineKeyboardButton("Сделать объявление...", callback_data='director_announcement')],
        [InlineKeyboardButton("Написать слона/педаль", callback_data='staff_write_something')],
        [InlineKeyboardButton("Попросить купить", callback_data='buy')],
        [InlineKeyboardButton("Узнать контакты", callback_data='director_employee_contacts')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с клавиатурой
    context.bot.send_message(chat_id=chat_id, text="Меню дирекции:", reply_markup=reply_markup)
    return DIRECTOR_ACTION

def show_staff_menu(update: Update, context: CallbackContext) -> int:
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
    context.bot.send_message(chat_id=chat_id, text="Меню сотрудников:", reply_markup=reply_markup)
    return STAFF_ACTION

def show_directions_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("НТН", callback_data='НТН')],
        [InlineKeyboardButton("НЕН", callback_data='НЕН')],
        [InlineKeyboardButton("НОН", callback_data='НОН')],
        [InlineKeyboardButton("НФН", callback_data='НФН')],
        [InlineKeyboardButton("Назад", callback_data='back_to_director')]  # Кнопка "Назад"
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите направление:", reply_markup=reply_markup)
    return CHOOSE_DIRECTION

def show_message_options(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Определяем, является ли пользователь дирекцией
    user = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    is_director = user and user.get('статус') == '0'

    keyboard = [
        [InlineKeyboardButton("...дирекции", callback_data='write_to_director')],
        [InlineKeyboardButton("...всем сотрудникам", callback_data='write_to_all_staff')],
        [InlineKeyboardButton("...всему направлению...", callback_data='write_to_department')],
        [InlineKeyboardButton("...вожатым команды...", callback_data='write_to_team_leaders')],
        [InlineKeyboardButton("...судьям турнира...", callback_data='write_to_tournament_judges')]
    ]

    # Добавляем кнопку "всем зондерам" только для дирекции
    if is_director:
        keyboard.insert(2, [InlineKeyboardButton("...всем зондерам", callback_data='write_to_zonders')])

    keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_previous_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите, кому отправить сообщение:", reply_markup=reply_markup)
    return CHOOSE_RECIPIENT

def show_team_leaders_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Греческий алфавит
    teams = [
        "Альфа", "Бета", "Гамма", "Дельта", "Эпсилон", "Эта", "Тета",
        "Йота", "Каппа", "Лямбда", "Мю", "Ню", "Кси", "Омикрон", "Пи", "Ро",
        "Сигма", "Тау", "Ипсилон", "Фи", "Хи", "Пси", "Омега"
    ]

    # Создаем кнопки для каждой команды
    keyboard = [
        [InlineKeyboardButton(team, callback_data=f'team_{team}')] for team in teams
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_message_options')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите команду:", reply_markup=reply_markup)
    return CHOOSE_TEAM

def show_tournament_judges_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Список турниров
    tournaments = ["ФМТ", "ГУТ", "БХТ"]

    # Создаем кнопки для каждого турнира
    keyboard = [
        [InlineKeyboardButton(tournament, callback_data=f'tournament_{tournament}')] for tournament in tournaments
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_message_options')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите турнир:", reply_markup=reply_markup)
    return CHOOSE_TOURNAMENT
