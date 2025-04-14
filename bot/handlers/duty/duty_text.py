from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
import asyncio
from your_google_sheet_module import async_read_google_sheet


async def handle_duty_text_input(update: Update, context: CallbackContext) -> int:
    duty_text = update.message.text.strip()

    # Кэширование данных
    if 'users_data' not in context.bot_data:
        try:
            context.bot_data['users_data'] = await async_read_google_sheet(TABULA)
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            await update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
            return ConversationHandler.END

    users_data = context.bot_data['users_data']

    # Проверка отправителя
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        await update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Проверка школьника
    selected_student = context.user_data.get('selected_student')
    if not selected_student:
        await update.message.reply_text("❌ Ошибка: данные школьника не найдены.")
        return ConversationHandler.END

    # Формирование сообщения
    message_text = (
        f"🚨 НАРЯД 🚨\n\n"
        f"КОМУ: {selected_student['имя']} {selected_student['фамилия']} ({selected_student['команда']})\n"
        f"ОТ КОГО: {sender['имя']} {sender['фамилия']} ({sender['команда']})\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{duty_text}"
    )

    # Получатели (кэшированные)
    recipients = [user for user in users_data if user.get('псин') == '1']
    if not recipients:
        await update.message.reply_text("❌ Нет назначенных сотрудников ПСИН.")
        return ConversationHandler.END

    # Асинхронная отправка
    send_tasks = [
        context.bot.send_message(chat_id=r['id'], text=message_text)
        for r in recipients
    ]
    
    results = await asyncio.gather(*send_tasks, return_exceptions=True)
    
    # Обработка ошибок отправки
    for r, result in zip(recipients, results):
        if isinstance(result, Exception):
            print(f"Ошибка отправки {r['id']}: {result}")

    await update.message.reply_text(f"✅ Запрос отправлен {len(recipients)} сотрудникам ПСИН!")
    return await show_staff_menu(update, context)
