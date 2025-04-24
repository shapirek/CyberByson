import logging
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from fuzzywuzzy import process

from bot.common import load_users_data_async
from bot.config import (
    INPUT_CHILD_NAME,
    CHOOSE_CHILD,
    INPUT_MESSAGE_FOR_CHILD,
)
from bot.utils.keyboards.parents_menu import show_parents_menu

logger = logging.getLogger(__name__)


async def handle_parent_call(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает кнопку «Пусть ребёнок мне позвонит!»: 
    спрашивает ФИО ребёнка.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Как зовут вашего ребёнка?")
    return INPUT_CHILD_NAME


async def handle_child_name_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Принимает ввод ФИО, ищет ребёнка в ранее загруженных kids_data
    и либо сразу идёт к вводу сообщения, либо предлагает выбрать из списка.
    """
    user_input = update.message.text.strip()
    parts = user_input.split()
    if len(parts) < 2:
        await update.message.reply_text("❌ Пожалуйста, введите имя и фамилию ребёнка.")
        return INPUT_CHILD_NAME

    # Данные детей были загружены в show_parents_menu
    kids_data = context.user_data.get('kids_data', [])
    if not kids_data:
        await update.message.reply_text("⚠️ Ошибка: данные школьников не найдены.")
        return ConversationHandler.END

    # Строим список для поиска
    lookup = [f"{kid['фамилия']} {kid['имя']}" for kid in kids_data]
    matches = process.extract(user_input, lookup, limit=5)
    filtered = [name for name, score in matches if score >= 70]

    if not filtered:
        await update.message.reply_text("❌ Ребёнок не найден. Попробуйте снова.")
        return INPUT_CHILD_NAME

    matched = [kid for kid in kids_data if f"{kid['фамилия']} {kid['имя']}" in filtered]

    # Если ровно один вариант
    if len(matched) == 1:
        context.user_data['selected_child'] = matched[0]
        await update.message.reply_text(
            f"✅ Выбран:\n{matched[0]['имя']} {matched[0]['фамилия']} ({matched[0]['команда']})"
        )
        await update.message.reply_text("Что нужно передать? Напишите сообщение:")
        return INPUT_MESSAGE_FOR_CHILD

    # Иначе — предлагаем выбрать
    keyboard = [
        [
            InlineKeyboardButton(
                f"{kid['фамилия']} {kid['имя']} {kid.get('отчество','')} ({kid['команда']})",
                callback_data=f"select_child_{i}"
            )
        ]
        for i, kid in enumerate(matched)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Найдено несколько вариантов. Выберите нужного:",
        reply_markup=reply_markup
    )
    context.user_data['matched_children'] = matched
    return CHOOSE_CHILD


async def handle_child_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Получает индекс выбранного ребёнка, сохраняет его и спрашивает сообщение.
    """
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[2])
    matched = context.user_data.get('matched_children', [])
    if idx < 0 or idx >= len(matched):
        await query.edit_message_text("❌ Ошибка: данные не найдены.")
        return ConversationHandler.END

    child = matched[idx]
    context.user_data['selected_child'] = child
    await query.edit_message_text(
        f"✅ Выбран:\n{child['имя']} {child['фамилия']} ({child['команда']})"
    )
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Что нужно передать? Напишите сообщение:"
    )
    return INPUT_MESSAGE_FOR_CHILD


async def handle_message_for_child_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Принимает текст от родителя и рассылает вожатым команды ребёнка.
    """
    message_text = update.message.text.strip()
    child = context.user_data.get('selected_child')
    if not child:
        await update.message.reply_text("❌ Ошибка: ребёнок не выбран.")
        return ConversationHandler.END

    # Загружаем всех пользователей (staff & others)
    users = await load_users_data_async()

    # Фильтруем вожатых по команде ребёнка
    team = child.get('команда')
    mentors = [u for u in users if u.get('команда') == team]
    if not mentors:
        await update.message.reply_text("❌ Нет вожатых для этой команды.")
        return await show_parents_menu(update, context)

    # Формируем сообщение
    send_text = (
        "🙏 ПЕРЕДАЮ ОТ РОДИТЕЛЕЙ 🙏\n\n"
        f"{child['имя']} {child['фамилия']}\n\n"
        "━━━━━━━━━━\n"
        f"{message_text}"
    )

    # Рассылаем пакетно
    import asyncio as _aio
    tasks = [
        context.bot.send_message(chat_id=int(m['id']), text=send_text)
        for m in mentors
    ]
    for i in range(0, len(tasks), 30):
        await _aio.gather(*tasks[i:i+30])
        if i + 30 < len(tasks):
            await _aio.sleep(1)

    await update.message.reply_text("✅ Сообщение отправлено вожатым команды!")
    return await show_parents_menu(update, context)
