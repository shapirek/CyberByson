import logging
from typing import List, Dict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .env import TABULA, TABULA_kids
from bot.config import (
    INPUT_STUDENT_INFO,
    CHOOSE_STUDENT,
    INPUT_DUTY_TEXT,
)
from bot.services.google_sheets.read_2 import read_google_sheet_sheet2
from bot.common import load_users_data_async
from bot.utils.keyboards.staff_menu import show_staff_menu
from fuzzywuzzy import process

logger = logging.getLogger(__name__)


async def handle_assign_duty(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает кнопку "Выдать наряд": спрашивает ФИО школьника.
    """
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    await context.bot.send_message(
        chat_id=chat_id,
        text="Введите имя и фамилию школьника:"
    )
    return INPUT_STUDENT_INFO


async def handle_student_info_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Принимает ФИО от пользователя, ищет родителей в Google Sheets
    и предлагает выбрать, если найдено несколько.
    """
    user_input = update.message.text.strip()

    parts = user_input.split()
    if len(parts) < 2:
        await update.message.reply_text("❌ Пожалуйста, введите имя и фамилию.")
        return INPUT_STUDENT_INFO

    # Загрузка списка родителей (в отдельном потоке, если функция синхронная)
    try:
        parents_data: List[Dict] = await read_google_sheet_sheet2(TABULA_kids)
    except Exception as e:
        logger.error(f"Ошибка загрузки данных школьников: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    # Собираем список "Фамилия Имя" для поиска
    lookup = [f"{p['фамилия']} {p['имя']}" for p in parents_data]
    matches = process.extract(user_input, lookup, limit=5)
    filtered = [name for name, score in matches if score >= 70]

    if not filtered:
        await update.message.reply_text("❌ Не найдено подходящих записей. Попробуйте еще раз.")
        return INPUT_STUDENT_INFO

    # Оставляем только совпавших
    matched = [p for p in parents_data if f"{p['фамилия']} {p['имя']}" in filtered]

    # Если один — сразу к вводу текста наряда
    if len(matched) == 1:
        context.user_data['selected_student'] = matched[0]
        await update.message.reply_text(
            f"✅ Наряд получит:\n\n"
            f"{matched[0]['фамилия']} {matched[0]['имя']} ({matched[0]['команда']})"
        )
        await update.message.reply_text("Укажите причину наряда:")
        return INPUT_DUTY_TEXT

    # Иначе — предлагаем выбрать
    keyboard = [
        [
            InlineKeyboardButton(
                f"{p['фамилия']} {p['имя']} {p['отчество']} ({p['команда']})",
                callback_data=f"select_student_{i}"
            )
        ]
        for i, p in enumerate(matched)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Найдено несколько вариантов. Выберите нужного:",
        reply_markup=reply_markup
    )
    context.user_data['matched_students'] = matched
    return CHOOSE_STUDENT


async def handle_student_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает выбор школьника из списка и спрашивает причину наряда.
    """
    query = update.callback_query
    await query.answer()

    idx = int(query.data.split("_")[2])
    matched = context.user_data.get('matched_students', [])
    if idx < 0 or idx >= len(matched):
        await query.edit_message_text("❌ Ошибка: данные не найдены.")
        return ConversationHandler.END

    student = matched[idx]
    context.user_data['selected_student'] = student

    await query.edit_message_text(
        f"✅ Наряд получит:\n\n"
        f"{student['фамилия']} {student['имя']} ({student['команда']})"
    )
    # Переходим к вводу текста наряда
    await context.bot.send_message(
        chat_id=query.message.chat_id, 
        text="Укажите причину наряда:"
    )
    return INPUT_DUTY_TEXT

async def handle_duty_text_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Принимает текст наряда, находит сотрудников ПСИН и рассылает им сообщение.
    Затем возвращает пользователя в меню сотрудников.
    """
    duty_text = update.message.text.strip()

    # 1) Загрузим и закешируем users_data
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()
    users = context.bot_data['users_data']

    # 2) Найдём отправителя по коду
    sender_code = str(context.user_data.get('code', ''))
    sender = next((u for u in users if str(u.get('код')) == sender_code), None)
    if not sender:
        await update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # 3) Получим выбранного школьника
    selected = context.user_data.get('selected_student')
    if not selected:
        await update.message.reply_text("❌ Ошибка: данные школьника не найдены.")
        return ConversationHandler.END

    # 4) Соберём текст наряда
    message_text = (
        "🚨 НАРЯД 🚨\n\n"
        f"КОМУ: {selected['имя']} {selected['фамилия']} ({selected['команда']})\n"
        f"ОТ КОГО: {sender['имя']} {sender['фамилия']} ({sender.get('команда','')})\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"{duty_text}"
    )

    # 5) Фильтруем сотрудников ПСИН (псин == '1')
    recipients = [u for u in users if u.get('псин') == '1']
    if not recipients:
        await update.message.reply_text("❌ Нет назначенных сотрудников ПСИН.")
        return ConversationHandler.END

    # 6) Асинхронно рассылаем всем ПСИН пакетно (по 30/сек)
    import asyncio
    tasks = [
        context.bot.send_message(chat_id=int(u['id']), text=message_text)
        for u in recipients
    ]
    for i in range(0, len(tasks), 30):
        await asyncio.gather(*tasks[i:i+30])
        if i + 30 < len(tasks):
            await asyncio.sleep(1)

    # 7) Уведомляем отправителя
    await update.message.reply_text("✅ Запрос отправлен всем сотрудникам ПСИН!")

    # 8) Возвращаем в меню сотрудников
    return await show_staff_menu(update, context)
