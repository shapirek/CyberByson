from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler


async def handle_child_choice(update: Update, context: CallbackContext) -> int:
    """
    Асинхронно обрабатывает выбор ребенка из списка.
    """
    query = update.callback_query
    await query.answer()

    try:
        # Извлекаем индекс с проверкой ошибок
        selected_idx = int(query.data.split('_')[2])
        matched_children = context.user_data.get('matched_children', [])
        
        if not matched_children or selected_idx >= len(matched_children):
            await query.edit_message_text("❌ Ошибка: неверный выбор ребенка.")
            return ConversationHandler.END

        # Сохраняем выбранного ребенка
        selected_child = matched_children[selected_idx]
        context.user_data['selected_child'] = selected_child

        # Объединенное сообщение с выбором и запросом
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"✅ Вы выбрали:\n\n"
                f"{selected_child['имя']} {selected_child['фамилия']} ({selected_child['команда']})\n\n"
                "Это сообщение будет направлено вожатым. Напишите, что нужно передать:"
        )
        
        # Удаляем сообщение с кнопками
        await query.delete_message()

        return INPUT_MESSAGE_FOR_CHILD

    except (ValueError, IndexError, AttributeError) as e:
        print(f"Ошибка обработки выбора: {e}")
        await query.edit_message_text("❌ Произошла ошибка. Попробуйте снова.")
        return ConversationHandler.END
