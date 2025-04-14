from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


async def handle_parent_call(update: Update, context: CallbackContext) -> int:
    """
    Асинхронно обрабатывает запрос звонка от ребенка.
    """
    query = update.callback_query
    await query.answer()
    
    try:
        await query.edit_message_text("Как зовут вашего ребенка?")
        return INPUT_CHILD_NAME
    except Exception as e:
        # Альтернативный вариант при ошибке редактирования
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Как зовут вашего ребенка?"
        )
        return INPUT_CHILD_NAME
