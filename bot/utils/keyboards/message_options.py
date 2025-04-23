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

from bot.config import CHOOSE_RECIPIENT
from bot.common import load_users_data_async  # Импорт функции загрузки данных

async def show_message_options(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    try:
        # Проверяем и загружаем данные пользователей
        if 'users_data' not in context.bot_data:
            context.bot_data['users_data'] = await load_users_data_async()
        
        users_data = context.bot_data['users_data']

        # Определяем пользователя
        user = next(
            (u for u in users_data 
             if str(u.get('код', '')) == str(context.user_data.get('code', ''))),
            None
        )
        
        is_director = user and user.get('статус') == '0'

        # Формируем клавиатуру
        keyboard = [
            [InlineKeyboardButton("...дирекции", callback_data='write_to_director')],
            [InlineKeyboardButton("...всем сотрудникам", callback_data='write_to_all_staff')],
            [InlineKeyboardButton("...всему направлению...", callback_data='write_to_department')],
            [InlineKeyboardButton("...вожатым команды...", callback_data='write_to_team_leaders')],
            [InlineKeyboardButton("...судьям турнира...", callback_data='write_to_tournament_judges')]
        ]

        # Добавляем специальную кнопку для дирекции
        if is_director:
            keyboard.insert(2, [InlineKeyboardButton("...всем зондерам", callback_data='write_to_zonders')])

        keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_previous_menu')])

        # Отправляем обновленное сообщение
        await query.edit_message_text(
            text="Выберите, кому отправить сообщение:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHOOSE_RECIPIENT

    except Exception as e:
        # Обработка ошибок
        await query.edit_message_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        logger.error(f"Error in show_message_options: {str(e)}")
        return ConversationHandler.END
