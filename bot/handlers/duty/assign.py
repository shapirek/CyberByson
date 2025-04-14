from telegram import Update
from telegram.ext import CallbackContext

def handle_assign_duty(update: Update, context: CallbackContext) -> int:
    """Обрабатывает нажатие кнопки 'Выдать наряд'."""
    query = update.callback_query
    query.answer()

    # Отправляем сообщение с инструкцией через бота
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Введите имя и фамилию школьника:"
    )

    return INPUT_STUDENT_INFO
