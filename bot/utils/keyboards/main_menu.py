import loggin

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Пользователь запустил /start: {update.effective_user.id}")
    keyboard = [
        ['Школьники', 'Сотрудники'],
        ['Родители'],
        ['Завершить диалог']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)

async def show_main_menu_in_chat(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    keyboard = [
        ['Школьники', 'Сотрудники'],
        ['Родители'],
        ['Завершить диалог']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await context.bot.send_message(chat_id=chat_id, text="Выберите категорию:", reply_markup=reply_markup)
