from telegram import Update
from telegram.ext import CallbackContext


def handle_request_equipment(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Запрашиваем у пользователя информацию о технике
    query.edit_message_text("Укажите, какая техника необходима, когда и куда ее принести:")

    # Переходим в состояние REQUEST_EQUIPMENT
    return REQUEST_EQUIPMENT
