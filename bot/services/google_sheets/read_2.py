def read_google_sheet_sheet2(sheet_url):
    """
    Загружает данные из второй таблицы (таблица школьников) Google Sheets.
    """
    if not sheet_url:
        raise Exception("TABULA_kids не задана — проверьте env-переменную")
     csv_url = sheet_url.replace('/edit', '/export?format=csv') 

     # Загружаем данные
     response = requests.get(csv_url)

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
    parents_data = []
    for row in reader:
        if len(row) >= 5:  # Убедимся, что строка содержит все необходимые колонки
            parent = {
                'фамилия': row[0],        # 1-ая колонка
                'имя': row[1],    # 2-ая колонка
                'отчество': row[2],   # 3-я колонка
                'команда': row[3],    # 4-ая колонка
                'контакты': row[4]    # 5-ая колонка
            }
            parents_data.append(parent)

    return parents_data
