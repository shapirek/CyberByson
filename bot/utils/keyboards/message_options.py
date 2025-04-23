from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import CHOOSE_RECIPIENT
from bot.common import load_users_data_async
import logging

logger = logging.getLogger(__name__)


async def show_message_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    try:
        # Загружаем данные пользователей, если ещё не загружены
        if 'users_data' not in context.bot_data:
            context.bot_data['users_data'] = await load_users_data_async()

        users_data = context.bot_data['users_data']
        user_code = str(context.user_data.get('code', ''))
        user = next((u for u in users_data if str(u.get('код')) == user_code), None)
        is_director = user and user.get('статус') == '0'

        keyboard = [
            [InlineKeyboardButton("...дирекции", callback_data='write_to_director')],
            [InlineKeyboardButton("...всем сотрудникам", callback_data='write_to_all_staff')],
            [InlineKeyboardButton("...всему направлению...", callback_data='write_to_department')],
            [InlineKeyboardButton("...вожатым команды...", callback_data='write_to_team_leaders')],
            [InlineKeyboardButton("...судьям турнира...", callback_data='write_to_tournament_judges')]
        ]

        if is_director:
            keyboard.insert(2, [InlineKeyboardButton("...всем зондерам", callback_data='write_to_zonders')])

        keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_previous_menu')])

        await query.edit_message_text(
            text="Выберите, кому отправить сообщение:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSE_RECIPIENT

    except Exception as e:
        logger.error(f"Ошибка в show_message_options: {e}")
        await query.edit_message_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END
