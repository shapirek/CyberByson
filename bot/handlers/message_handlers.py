from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.config import WAIT_FOR_RESPONSE

async def handle_input_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Хендлер, сохраняющий введённый текст и спрашивающий,
    нужно ли ждать ответ (кнопки «Да»/«Нет»).
    """
    # 1) Сохраняем текст
    message_text = update.message.text
    context.user_data['message_text'] = message_text

    # 2) Клавиатура «Да» / «Нет»
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='wait_for_response_yes')],
        [InlineKeyboardButton("Нет", callback_data='wait_for_response_no')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 3) Отправляем вопрос
    await update.message.reply_text(
        "Ждете ответа?",
        reply_markup=reply_markup
    )

    # 4) Переходим в состояние ожидания
    return WAIT_FOR_RESPONSE
