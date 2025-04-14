from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler


async def handle_tournament_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    # Оптимизация через match-case (Python 3.10+)
    match data.split('_'):
        case ['tournament', tournament]:
            context.user_data.update({
                'selected_tournament': tournament,
                'recipient_type': 'tournament_judges'
            })
            await query.edit_message_text(text=f"Введите сообщение для судей {tournament}:")
            return INPUT_MESSAGE
            
        case _ if data == 'back_to_message_options':
            return await show_message_options(update,context)
            
        case _:
            await query.edit_message_text("❌ Неизвестный турнир.")
            return ConversationHandler.END
