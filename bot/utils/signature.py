def format_message_with_signature(message_text: str, sender_name: str, sender_surname: str, sender_status: str, recipient_type: str = None, **kwargs) -> str:
    """
    Формирует сообщение с подписью и тегами, без экранирования Markdown-разметки.
    """
    # Генерация тегов
    tags = generate_tags(message_text)

    # Определяем префикс в зависимости от типа получателя
    if recipient_type == 'director':
        prefix = "Дорогая дирекция!\n\n"
    elif recipient_type == 'all_staff':
        prefix = "Летняя Школа!\n\n"
    elif recipient_type == 'tournament_judges':
        prefix = f"Дорогие судьи {kwargs.get('tournament')}!\n\n"
    elif kwargs.get('direction'):
        prefix = f"Сотрудники {kwargs.get('direction')}!\n\n"
    elif kwargs.get('team'):
        prefix = f"Вожатые команды {kwargs.get('team')}!\n\n"
    else:
        prefix = ""

    # Определяем заголовок в зависимости от типа сообщения
    if recipient_type == 'equipment_request':  # Запрос техники
        header = "📢 ЗАПРОС ТЕХНИКИ 📢\n\n"
    elif sender_status == '0':  # Если отправитель — дирекция
        header = "❗️ ОБЪЯВЛЕНИЕ ❗️\n\n"
    else:  # Если отправитель — не дирекция
        header = "📨 НОВОЕ СООБЩЕНИЕ 📨\n\n"

    # Формируем итоговое сообщение
    formatted_message = (
        f"{header}"  # Заголовок
        f"{prefix}"  # Приписка после заголовка
        f"{message_text}\n\n"
        f"С уважением,\n"
        f"{sender_name} {sender_surname}"
    )

    return formatted_message
