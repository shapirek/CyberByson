from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

async def handle_category(update: Update, context: CallbackContext) -> int:
    category = update.message.text
    if category == 'Завершить диалог':
        await update.message.reply_text("Диалог завершён. До новых встреч!")
        return ConversationHandler.END
    
    handlers = {
        'Родители': show_parents_menu,
        'Школьники': show_students_menu,
        'Сотрудники': handle_employees
    }
    
    handler = handlers.get(category)
    if handler:
        return await handler(update, context)
    
    return ConversationHandler.END

async def handle_employees(update: Update, context: CallbackContext) -> int:
    try:
        # Загружаем асинхронно и сохраняем в context
        context.bot_data['users_data'] = await async_read_google_sheet(TABULA)
        print("Данные успешно загружены!")
        await update.message.reply_text("Укажите Ваш код доступа:")
        return CODE_INPUT
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        await update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END
