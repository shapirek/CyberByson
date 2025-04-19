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

# bot/common.py
import aiohttp
import csv
import chardet
from io import StringIO
from typing import List, Dict
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10  # секунд
CACHE_TTL = 300  # 5 минут

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
    if not hasattr(_parse_and_cache, 'cache_info'):
        return None
        
    cache_info = _parse_and_cache.cache_info()
    if cache_info.hits > 0 and cache_info.ttl > 0:
        return _parse_and_cache.cache_info()._CacheInfo__cache[list(_parse_and_cache.cache_info()._CacheInfo__cache.keys())[0]]
    return None

def get_fallback_data() -> List[Dict]:
    """Резервные данные на случай ошибок"""
    # Можно добавить логику чтения из локального файла
    return []
