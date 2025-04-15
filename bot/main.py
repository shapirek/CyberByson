import csv
from io import StringIO
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import chardet
import time
import logging
from datetime import datetime, timedelta
from telegram.utils.helpers import escape_markdown

import yake
import uuid
from fuzzywuzzy import process

import pytz

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext
import logging

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Определение состояний для ConversationHandler
(
    CODE_INPUT,
    DIRECTOR_ACTION,
    STAFF_ACTION,
    STUDENTS_ACTION,
    PARENTS_ACTION,
    CHOOSE_RECIPIENT,
    INPUT_MESSAGE,
    WAIT_FOR_RESPONSE,
    CHOOSE_DIRECTION,
    CHOOSE_TEAM,
    CHOOSE_TOURNAMENT,
    REQUEST_EQUIPMENT,
    INPUT_STUDENT_INFO,
    CHOOSE_STUDENT,
    INPUT_DUTY_TEXT,
    INPUT_CHILD_NAME,
    CHOOSE_CHILD,
    INPUT_MESSAGE_FOR_CHILD
) = range(18)

# Колбэк для команды /start
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Привет! Я готов к работе!")
    return ConversationHandler.END

# Колбэк для кнопок
async def inline_button_handler(update: Update, context: CallbackContext) -> None:
    # Логика обработки инлайн кнопок
    await update.callback_query.answer()

# Колбэк для кнопки "Проблема решена!"
async def handle_problem_solved_button(update: Update, context: CallbackContext) -> None:
    # Логика для обработки кнопки "Проблема решена!"
    await update.callback_query.answer()

# Пример обработки новостей
async def handle_news(update: Update, context: CallbackContext) -> None:
    # Логика для обработки новостей
    await update.callback_query.answer("Новости обработаны!")

# Колбэк для ввода кода
async def handle_code_input(update: Update, context: CallbackContext) -> int:
    code = update.message.text
    # Логика обработки кода
    await update.message.reply_text(f"Вы ввели код: {code}")
    return CODE_INPUT  # Переход к следующему состоянию

# Колбэк для выбора получателя
async def handle_recipient_choice(update: Update, context: CallbackContext) -> int:
    recipient = update.callback_query.data
    # Логика обработки выбора получателя
    await update.callback_query.answer(f"Вы выбрали: {recipient}")
    return CHOOSE_RECIPIENT

# Пример обработки сообщения
async def handle_input_message(update: Update, context: CallbackContext) -> int:
    message_text = update.message.text
    # Логика обработки сообщения
    await update.message.reply_text(f"Сообщение: {message_text}")
    return INPUT_MESSAGE

# Основная асинхронная функция
async def main() -> None:
    # Создаем приложение с асинхронной версией
    application = Application.builder().token(TOKEN).build()

    # Обработчик для кнопки "Проблема решена!"
    application.add_handler(CallbackQueryHandler(handle_problem_solved_button, pattern=r'^problem_solved_'))

    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.text & ~Filters.command, inline_button_handler),
            CallbackQueryHandler(inline_button_handler)
        ],
        states={
            CODE_INPUT: [MessageHandler(Filters.text, handle_code_input)],
            DIRECTOR_ACTION: [CallbackQueryHandler(inline_button_handler)],
            STAFF_ACTION: [CallbackQueryHandler(inline_button_handler)],
            STUDENTS_ACTION: [CallbackQueryHandler(inline_button_handler)],
            PARENTS_ACTION: [CallbackQueryHandler(inline_button_handler)],
            CHOOSE_RECIPIENT: [CallbackQueryHandler(handle_recipient_choice)],
            INPUT_MESSAGE: [MessageHandler(Filters.text & ~Filters.command, handle_input_message)],
            WAIT_FOR_RESPONSE: [CallbackQueryHandler(inline_button_handler)],
            CHOOSE_DIRECTION: [CallbackQueryHandler(inline_button_handler)],
            CHOOSE_TEAM: [CallbackQueryHandler(inline_button_handler)],
            CHOOSE_TOURNAMENT: [CallbackQueryHandler(inline_button_handler)],
            REQUEST_EQUIPMENT: [MessageHandler(Filters.text & ~Filters.command, inline_button_handler)],
            INPUT_STUDENT_INFO: [MessageHandler(Filters.text & ~Filters.command, inline_button_handler)],
            CHOOSE_STUDENT: [CallbackQueryHandler(inline_button_handler, pattern=r'^select_student_\d+$')],
            INPUT_DUTY_TEXT: [MessageHandler(Filters.text & ~Filters.command, inline_button_handler)],
            INPUT_CHILD_NAME: [MessageHandler(Filters.text & ~Filters.command, inline_button_handler)],
            CHOOSE_CHILD: [CallbackQueryHandler(inline_button_handler, pattern=r'^select_child_\d+$')],
            INPUT_MESSAGE_FOR_CHILD: [MessageHandler(Filters.text & ~Filters.command, inline_button_handler)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    # Добавляем ConversationHandler в приложение
    application.add_handler(conv_handler)

    # Дополнительные обработчики callback_query
    application.add_handler(CallbackQueryHandler(handle_news, pattern='^news$'))
    application.add_handler(CallbackQueryHandler(inline_button_handler))

    # Запуск бота
    await application.run_polling()

if name == '__main__':
    import asyncio
    asyncio.run(main())
