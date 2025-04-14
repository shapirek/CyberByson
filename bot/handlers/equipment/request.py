from telegram import Update
from telegram.ext import CallbackContext
import asyncio


async def handle_request_equipment(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    
    try:
        await query.answer()
        await query.edit_message_text(
            "Укажите, какая техника необходима, когда и куда ее принести:"
        )
        return REQUEST_EQUIPMENT
        
    except Exception as e:
        print(f"Ошибка при запросе оборудования: {e}")
        # Попытка отправить новое сообщение, если редактирование не удалось
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Укажите, какая техника необходима, когда и куда ее принести:"
        )
        return REQUEST_EQUIPMENT
