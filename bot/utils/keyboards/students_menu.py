from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from bot.config import STUDENTS_ACTION


async def show_students_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Что такое КЛШ?", callback_data='student_info')],
        [InlineKeyboardButton("Как попасть в КЛШ?", callback_data='student_how_to')],
        [InlineKeyboardButton("Буклет этого года", callback_data='student_booklet')],
        [InlineKeyboardButton("Архив КЛШ", callback_data='student_archive')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text("Что тебя интересует?", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Что тебя интересует?", reply_markup=reply_markup)

    return STUDENTS_ACTION
