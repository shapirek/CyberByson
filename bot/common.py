from bot.services.google_sheets.read_1 import read_google_sheet
from bot.services.google_sheets.read_2 import read_google_sheet_sheet2
from bot.services.google_sheets.read_schedule import read_schedule_sheet

from bot.env import TOKEN
from bot.env import TABULA
from bot.env import TABULA_kids
from bot.env import SCHEDULE_SHEET_URL
from bot.env import CHANNEL_ID
from bot.env import CHANNEL_LINK_PART
from bot.env import GROUP_ID
from bot.env import TIMEZONE

# bot/common.py
import aiohttp
import csv
import chardet
from io import StringIO
from typing import List, Dict
import logging
from functools import lru_cache

REQUEST_TIMEOUT = 10  # секунд
CACHE_TTL = 300  # 5 минут

# Настройка логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def load_users_data_async() -> List[Dict[str, str]]:
    """
    Асинхронно загружает и парсит данные пользователей из Google Sheets
    с кэшированием и обработкой ошибок.
    
    Returns:
        List[Dict]: Список пользователей с ключами по колонкам таблицы
    """
    try:
        # Пытаемся получить кэшированные данные
        if cached := get_cached_users_data():
            return cached
            
        data = await _fetch_raw_data()
        return _parse_and_cache(data)
        
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {str(e)}")
        return get_fallback_data()

@lru_cache(maxsize=1)
def _parse_and_cache(csv_data: str) -> List[Dict[str, str]]:
    """Парсинг и кэширование данных"""
    reader = csv.DictReader(StringIO(csv_data))
    return [{
        'код': row.get('код', ''),
        'id': row.get('id', ''),
        'имя': row.get('имя', ''),
        'фамилия': row.get('фамилия', ''),
        'статус': row.get('статус', ''),
        'направление': row.get('направление', ''),
        'команда': row.get('команда', ''),
        'судья': row.get('судья', ''),
        'технозондер': row.get('технозондер', ''),
        'псин': row.get('псин', '')
    } for row in reader]

async def _fetch_raw_data() -> str:
    """Асинхронная загрузка сырых данных"""
    csv_url = TABULA.replace('/edit', '/export?format=csv')
    
    async with aiohttp.ClientSession() as session:
        async with session.get(csv_url, timeout=REQUEST_TIMEOUT) as response:
            if response.status != 200:
                raise Exception(f"HTTP ошибка {response.status}")
                
            raw_data = await response.read()
            encoding = chardet.detect(raw_data)['encoding']
            return raw_data.decode(encoding)

def get_cached_users_data() -> List[Dict]:
    """Получение кэшированных данных с проверкой TTL"""
    if not hasattr(_parse_and_cache, 'cache'):
        return None

    cache = getattr(_parse_and_cache, 'cache')
    # Если в cache есть хотя бы один элемент — возвращаем его
    if len(cache) > 0:
        # берём значение первого ключа
        return next(iter(cache.values()))
   return None

def get_fallback_data() -> List[Dict]:
    """Резервные данные на случай ошибок"""
    # Можно добавить логику чтения из локального файла
    return []
