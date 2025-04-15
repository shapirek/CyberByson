def read_google_sheet(sheet_url):
    # Заменяем часть URL для экспорта в CSV
    csv_url = sheet_url.replace('/edit', '/export?format=csv')

    # Загружаем данные
    response = requests.get(csv_url)
    if response.status_code != 200:
        raise Exception("Не удалось загрузить таблицу. Проверьте ссылку и доступ.")

    # Определяем кодировку данных
    raw_data = response.content
    encoding = chardet.detect(raw_data)['encoding']

    # Декодируем данные с использованием определенной кодировки
    decoded_data = raw_data.decode(encoding)

    # Читаем CSV
    csv_data = StringIO(decoded_data)
    reader = csv.reader(csv_data)

    # Преобразуем данные в список словарей с указанием индексов колонок
    users_data = []
    for row in reader:
        if len(row) >= 9:  # Убедимся, что строка содержит все необходимые колонки
            user = {
                'код': row[0],        # 1-ая колонка
                'id': row[1],         # 2-ая колонка (ID телеграма)
                'имя': row[2],        # 3-я колонка
                'фамилия': row[3],    # 4-ая колонка (фамилия)
                'статус': row[4],     # 5-ая колонка
                'направление': row[5], # 6-ая колонка
                'команда': row[6],    # 7-ая колонка (команда)
                'судья': row[7],      # 8-ая колонка (судья)
                'технозондер': row[8], # 9-ая колонка (технозондер)
                'псин': row[9] # 10-ая колонка (псин)
            }
            users_data.append(user)

    return users_data
