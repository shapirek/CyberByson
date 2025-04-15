import logging
from bot.services.google_sheets.read_1 import read_google_sheet
from bot.services.google_sheets.read_2 import read_google_sheet_sheet2
from bot.services.google_sheets.read_schedule import read_schedule_sheet

from .env import TOKEN
from .env import TABULA
from .env import TABULA_kids
from .env import SCHEDULE_SHEET_URL
from .env import CHANNEL_ID
from .env import CHANNEL_LINK_PART
from .env import GROUP_ID
from .env import TIMEZONE


# Настройка логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

kids_data = await read_google_sheet_sheet2(TABULA_kids)
users_data = await read_google_sheet(TABULA)
parents_data = await read_google_sheet_sheet2(TABULA_kids)
staff_data = await read_google_sheet(TABULA)
schedule_data = await read_schedule_sheet(SCHEDULE_SHEET_URL)
