from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


async def handle_team_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith('team_'):
        team = data.split('_')[1]
        context.user_data.update({
            'selected_team': team,
            'recipient_type': 'team'
        })
        await query.edit_message_text(text=f"Введите сообщение для команды {team}:")
        return INPUT_MESSAGE
        
    if data == 'back_to_message_options':
        return await show_message_options(update, context)
        
    await query.edit_message_text("❌ Неизвестная команда.")
    return ConversationHandler.END
