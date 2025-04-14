def handle_news(update: Update, context: CallbackContext) -> None:
    """
    Обрабатывает нажатие кнопки НОВОСТИ с учетом форматов дат
    """
    try:
        # Получаем объект сообщения
        if update.callback_query:
            query = update.callback_query
            message = query.message
            query.answer()  # Убираем часики у кнопки
        else:
            message = update.message

        # Загрузка и подготовка данных
        schedule_data = read_schedule_sheet(SCHEDULE_SHEET_URL)
        current_date = get_current_date()

        # Поиск по нормализованным датам
        today_schedule = None
        for item in schedule_data:
            if 'дата' in item and normalize_table_date(item['дата']) == current_date:
                today_schedule = item
                break

        # Формирование ответа
        if not today_schedule:
            response_text = "📭 На сегодня новостей нет!"
            logger.warning(f"Не найдено расписание для даты: {current_date}")
        else:
            response_text = format_schedule_message(today_schedule, schedule_data)
            logger.info(f"Успешно загружено расписание на {current_date}")

        # Отправка ответа
        if update.callback_query:
            context.bot.send_message(
                chat_id=message.chat_id,
                text=response_text,
                parse_mode='Markdown'
            )
        else:
            message.reply_text(response_text, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Ошибка в handle_news: {str(e)}", exc_info=True)
        error_msg = "⚠️ Не удалось загрузить расписание. Попробуйте позже."
        if update.callback_query:
            update.callback_query.answer(error_msg, show_alert=True)
        else:
            update.message.reply_text(error_msg)
