from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import asyncio  # Для асинхронной версии
from functools import partial  # Для частичного применения функций


async def handle_message_for_child_input(update: Update, context: CallbackContext) -> int:
    """
    Асинхронно обрабатывает и отправляет сообщение для ребенка вожатым.
    """
    message_text = update.message.text.strip()

    # Проверка данных ребенка
    if not (selected_child := context.user_data.get('selected_child')):
        await update.message.reply_text("❌ Ошибка: данные ребенка не найдены.")
        return ConversationHandler.END

    # Кэширование данных сотрудников
    if 'staff_data' not in context.bot_data:
        try:
            context.bot_data['staff_data'] = await async_read_google_sheet(TABULA)
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            await update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
            return ConversationHandler.END

    staff_data = context.bot_data['staff_data']
    
    # Проверка команды ребенка
    if not (child_team := selected_child.get('команда')):
        await update.message.reply_text("❌ Ошибка: не удалось определить команду ребенка.")
        return ConversationHandler.END

    # Поиск вожатых команды
    matched_staff = [staff for staff in staff_data if staff.get('команда') == child_team]
    
    if not matched_staff:
        await update.message.reply_text("❌ Не найдено вожатых для команды ребенка.")
        return ConversationHandler.END

    # Формирование сообщения
    message_for_staff = (
        f"🙏 РОДИТЕЛИ ПЕРЕДАЮТ 🙏\n\n"
        f"{selected_child['имя']} {selected_child['фамилия']}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{message_text}"
    )

    # Асинхронная массовая отправка
    send_tasks = [
        context.bot.send_message(
            chat_id=staff['id'],
            text=message_for_staff
        )
        for staff in matched_staff
    ]
    
    # Обработка результатов отправки
    results = await asyncio.gather(*send_tasks, return_exceptions=True)
    successful_sends = sum(1 for r in results if not isinstance(r, Exception))
    
    for staff, result in zip(matched_staff, results):
        if isinstance(result, Exception):
            print(f"Ошибка отправки {staff['id']}: {result}")

    await update.message.reply_text(f"✅ Сообщение отправлено {successful_sends}/{len(matched_staff)} вожатым!")
    return await show_parents_menu(update, context)
