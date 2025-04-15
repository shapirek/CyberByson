import uuid
import yake


def generate_unique_id() -> str:
    """
    Генерирует уникальный идентификатор для каждого сообщения.
    """
    return str(uuid.uuid4())

def generate_tags(text: str) -> str:
    """
    Генерирует теги из текста с помощью YAKE!.
    Возвращает строку с тегами, разделёнными пробелами.
    """
    # Инициализация YAKE!
    kw_extractor = yake.KeywordExtractor(lan="ru", n=5, dedupLim=0.5, windowsSize=15)

    # Извлечение ключевых слов
    keywords = kw_extractor.extract_keywords(text)

    # Сортировка по весу (от меньшего к большему) и выбор одного тега
    if keywords:
        sorted_keywords = sorted(keywords, key=lambda x: x[1])
        best_tag = sorted_keywords[0][0]  # Выбираем самый релевантный тег

        # Убираем символы, которые могут нарушить Markdown-разметку
        best_tag_cleaned = best_tag.replace('*', '').replace('_', '').replace('[', '').replace(']', '')

        # Заменяем пробелы на подчёркивания и формируем тег
        return f"#{best_tag_cleaned.replace(' ', '_')}"
    else:
        return ""
