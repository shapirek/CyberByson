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

from bot.config import STUDENTS_ACTION


async def show_students_menu(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Что такое КЛШ?", callback_data='student_info')],
        [InlineKeyboardButton("Как попасть в КЛШ?", callback_data='student_how_to')],
        [InlineKeyboardButton("Буклет этого года", callback_data='student_booklet')],
        [InlineKeyboardButton("Архив КЛШ", callback_data='student_archive')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите опцию для школьников:", reply_markup=reply_markup)
    return STUDENTS_ACTION  # Возвращаем состояние меню школьников
