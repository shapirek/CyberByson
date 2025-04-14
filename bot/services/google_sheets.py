import requests
import chardet
import csv
from io import StringIO
from typing import List, Dict
from your_date_utils import normalize_table_date  # ваш модуль для работы с датами


import aiohttp
from aiohttp import ClientTimeout

async def async_read_google_sheet(sheet_url: str, gid: str = None) -> List[Dict]:
    """Универсальная асинхронная функция для чтения Google Sheets"""
    base_url = sheet_url.replace('/edit', '/export?format=csv')
    url = f"{base_url}&gid={gid}" if gid else base_url
    
    timeout = ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Ошибка загрузки: {response.status}")
            
            raw_data = await response.read()
            encoding = chardet.detect(raw_data)['encoding']
            decoded_data = raw_data.decode(encoding)
            
            return list(csv.DictReader(decoded_data.splitlines()))

from functools import lru_cache
import time

@lru_cache(maxsize=3)
def read_google_sheet_cached(sheet_url: str) -> List[Dict]:
    """Кэширование на 5 минут"""
    return read_google_sheet(sheet_url)

def parse_sheet_data(reader, columns_mapping: Dict) -> List[Dict]:
    """Универсальный парсер для разных листов"""
    return [
        {key: row[idx] for key, idx in columns_mapping.items() if idx < len(row)}
        for row in reader
    ]

def read_google_sheet(sheet_url: str) -> List[Dict]:
    columns_mapping = {
        'код': 0, 'id': 1, 'имя': 2, 
        'фамилия': 3, 'статус': 4, 'направление': 5,
        'команда': 6, 'судья': 7, 'технозондер': 8, 'псин': 9
    }
    return _read_sheet(sheet_url, columns_mapping)

def read_google_sheet_sheet2(sheet_url: str) -> List[Dict]:
    columns_mapping = {
        'фамилия': 0, 'имя': 1, 'отчество': 2,
        'команда': 3, 'контакты': 4
    }
    return _read_sheet(sheet_url, columns_mapping, gid="GID_kids")

def _read_sheet(sheet_url: str, columns_mapping: Dict, gid: str = None) -> List[Dict]:
    """Базовая функция для чтения листов"""
    csv_url = sheet_url.replace('/edit', '/export?format=csv')
    if gid:
        csv_url += f"&gid={gid}"
    
    response = requests.get(csv_url, timeout=10)
    response.raise_for_status()
    
    raw_data = response.content
    encoding = chardet.detect(raw_data)['encoding']
    decoded_data = raw_data.decode(encoding)
    
    reader = csv.reader(decoded_data.splitlines())
    next(reader)  # Пропускаем заголовок
    
    return parse_sheet_data(reader, columns_mapping)
