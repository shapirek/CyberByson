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

def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # 1. Первым регистрируем обработчик для кнопки "Проблема решена!"
    dp.add_handler(CallbackQueryHandler(handle_problem_solved_button, pattern=r'^problem_solved_'))

    # Настраиваем ConversationHandler для обработки состояний (например, ввода кодов доступа)
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.text & ~Filters.command, handle_category),
            CallbackQueryHandler(inline_button_handler)
        ],
        states={
            CODE_INPUT: [MessageHandler(Filters.text, handle_code_input)],
            DIRECTOR_ACTION: [CallbackQueryHandler(inline_button_handler)],
            STAFF_ACTION: [CallbackQueryHandler(inline_button_handler)],
            STUDENTS_ACTION: [CallbackQueryHandler(inline_button_handler)],  # Добавлено
            PARENTS_ACTION: [CallbackQueryHandler(inline_button_handler)],  # Добавлено
            CHOOSE_RECIPIENT: [CallbackQueryHandler(handle_recipient_choice)],
            INPUT_MESSAGE: [MessageHandler(Filters.text & ~Filters.command, handle_input_message)],
            WAIT_FOR_RESPONSE: [CallbackQueryHandler(handle_wait_for_response)],
            CHOOSE_DIRECTION: [CallbackQueryHandler(handle_direction_choice)],
            CHOOSE_TEAM: [CallbackQueryHandler(handle_team_choice)],
            CHOOSE_TOURNAMENT: [CallbackQueryHandler(handle_tournament_choice)],
            REQUEST_EQUIPMENT: [MessageHandler(Filters.text & ~Filters.command, handle_equipment_input)],
            INPUT_STUDENT_INFO: [MessageHandler(Filters.text & ~Filters.command, handle_student_info_input)],
            CHOOSE_STUDENT: [CallbackQueryHandler(handle_student_choice, pattern=r'^select_student_\d+$')],
            INPUT_DUTY_TEXT: [MessageHandler(Filters.text & ~Filters.command, handle_duty_text_input)],
            INPUT_CHILD_NAME: [MessageHandler(Filters.text & ~Filters.command, handle_child_name_input)],
            CHOOSE_CHILD: [CallbackQueryHandler(handle_child_choice, pattern=r'^select_child_\d+$')],
            INPUT_MESSAGE_FOR_CHILD: [MessageHandler(Filters.text & ~Filters.command, handle_message_for_child_input)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)

    # Добавляем обработчик для кнопки "Проблема решена!" с высоким приоритетом
    dp.add_handler(CallbackQueryHandler(handle_problem_solved_button, pattern='^problem_solved_'))

    dp.add_handler(CallbackQueryHandler(handle_news, pattern='^news$'))

    # Добавляем общий обработчик для остальных callback_data
    dp.add_handler(CallbackQueryHandler(inline_button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
