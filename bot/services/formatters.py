import uuid
import yake
from typing import Optional

# ————————————————————————————————
# 1) Unique ID generator
# ————————————————————————————————
def generate_unique_id() -> str:
    """
    Возвращает новый UUID в виде строки.
    """
    return str(uuid.uuid4())


# ————————————————————————————————
# 2) YAKE!-based tag extractor
# ————————————————————————————————
def generate_tags(text: str) -> str:
    """
    Извлекает ключевое слово из текста с помощью YAKE! и возвращает
    его в виде #tag (без спецсимволов Markdown).
    """
    if not text:
        return ""

    kw_extractor = yake.KeywordExtractor(
        lan="ru", n=5, dedupLim=0.5, windowsSize=15
    )
    keywords = kw_extractor.extract_keywords(text)
    if not keywords:
        return ""

    # берём самое релевантное
    best_tag = sorted(keywords, key=lambda x: x[1])[0][0]
    cleaned = best_tag.replace("*", "").replace("_", "") \
                      .replace("[", "").replace("]", "")
    return "#" + cleaned.replace(" ", "_")


# ————————————————————————————————
# 3) Async message‐with‐signature formatter
# ————————————————————————————————
async def format_message_with_signature_async(
    message_text: str,
    sender_name: str,
    sender_surname: str,
    sender_status: str,
    recipient_type: Optional[str] = None,
    **kwargs
) -> str:
    """
    Асинхронно формирует текст сообщения с шапкой, префиксом,
    телом, тегами и подписью, без экранирования Markdown.
    """
    # 1) Header
    if recipient_type == "equipment_request":
        header = "📢 ЗАПРОС ТЕХНИКИ 📢\n\n"
    elif sender_status == "0":
        header = "❗️ ОБЪЯВЛЕНИЕ ❗️\n\n"
    else:
        header = "📨 НОВОЕ СООБЩЕНИЕ 📨\n\n"

    # 2) Prefix by recipient
    if recipient_type == "director":
        prefix = "Дорогая дирекция!\n\n"
    elif recipient_type == "all_staff":
        prefix = "Летняя Школа!\n\n"
    elif recipient_type == "tournament_judges" and kwargs.get("tournament"):
        prefix = f"Дорогие судьи {kwargs['tournament']}!\n\n"
    elif kwargs.get("direction"):
        prefix = f"Сотрудники {kwargs['direction']}!\n\n"
    elif kwargs.get("team"):
        prefix = f"Вожатые команды {kwargs['team']}!\n\n"
    else:
        prefix = ""

    # 3) Tags
    tags = generate_tags(message_text)

    # 4) Assemble
    formatted = (
        f"{header}"
        f"{prefix}"
        f"{message_text}\n\n"
        f"{tags}\n\n" if tags else f"{header}{prefix}"
    )
    formatted += (
        "С уважением,\n"
        f"{sender_name} {sender_surname}"
    )
    return formatted
