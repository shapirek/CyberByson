def read_schedule_sheet(sheet_url: str) -> list:
    """
    Читает данные из таблицы расписания с нормализацией дат
    """
    csv_url = sheet_url.replace('/edit', '/export?format=csv')

    try:
        response = requests.get(csv_url)
        response.raise_for_status()

        raw_data = response.content
        encoding = chardet.detect(raw_data)['encoding']
        decoded_data = raw_data.decode(encoding)

        reader = csv.DictReader(decoded_data.splitlines())

        # Нормализуем даты в каждой строке
        normalized_data = []
        for row in reader:
            if 'дата' in row:
                row['дата'] = normalize_table_date(row['дата'])
            normalized_data.append(row)

        return normalized_data

    except Exception as e:
        raise Exception(f"Ошибка загрузки расписания: {str(e)}")
