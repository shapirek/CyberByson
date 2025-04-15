from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from bot.config import CHOOSE_RECIPIENT
from bot.common import users_data


async def show_message_options(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    # Определяем, является ли пользователь дирекцией
    user = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    is_director = user and user.get('статус') == '0'

    keyboard = [
        [InlineKeyboardButton("...дирекции", callback_data='write_to_director')],
        [InlineKeyboardButton("...всем сотрудникам", callback_data='write_to_all_staff')],
        [InlineKeyboardButton("...всему направлению...", callback_data='write_to_department')],
        [InlineKeyboardButton("...вожатым команды...", callback_data='write_to_team_leaders')],
        [InlineKeyboardButton("...судьям турнира...", callback_data='write_to_tournament_judges')]
    ]

    # Добавляем кнопку "всем зондерам" только для дирекции
    if is_director:
        keyboard.insert(2, [InlineKeyboardButton("...всем зондерам", callback_data='write_to_zonders')])

    keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_previous_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Выберите, кому отправить сообщение:", reply_markup=reply_markup)
    return CHOOSE_RECIPIENT
