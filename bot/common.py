import logging
from bot.services.google_sheets.read_1 import read_google_sheet
from bot.services.google_sheets.read_2 import read_google_sheet_sheet2
from bot.services.google_sheets.read_schedule import read_schedule_sheet


# Настройка логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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

kids_data = await read_google_sheet_sheet2(TABULA_kids)
users_data = await read_google_sheet(TABULA)
parents_data = await read_google_sheet_sheet2(TABULA_kids)
staff_data = await read_google_sheet(TABULA)
schedule_data = await read_schedule_sheet(SCHEDULE_SHEET_URL)
