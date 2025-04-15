def get_current_date() -> str:
    """Возвращает текущую дату в формате 'd.mm' (например '8.04')"""
    now = datetime.now(TIMEZONE)
    return f"{now.day}.{now.month:02d}"

def normalize_table_date(date_str: str) -> str:
    """
    Приводит даты из таблицы к единому формату 'd.mm'
    Примеры:
      '8.04' -> '8.04'
      '08.04' -> '8.04'
      '8.4' -> '8.04'
    """
    try:
        day, month = map(int, date_str.split('.'))
        return f"{day}.{month:02d}"
    except:
        return date_str  # если не удалось разобрать, оставляем как есть
