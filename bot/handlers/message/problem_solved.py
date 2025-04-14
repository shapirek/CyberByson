from telegram import Update
from telegram.ext import CallbackContext
import asyncio


async def handle_problem_solved_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    print(f"[DEBUG] Callback data: {query.data}")

    if not query.data.startswith('problem_solved_'):
        return

    unique_id = query.data.split('_')[2]
    await handle_problem_solved(update, context, unique_id)

async def handle_problem_solved(update: Update, context: CallbackContext, unique_id: str) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем данные сообщения
    message_data = context.user_data.get(unique_id, {})
    if not message_data:
        await query.edit_message_text("❌ Ошибка: данные сообщения не найдены.")
        return

    # Параллельное удаление сообщений
    delete_tasks = []
    if 'channel_message_id' in message_data:
        delete_tasks.append(
            context.bot.delete_message(
                chat_id=CHANNEL_ID,
                message_id=message_data['channel_message_id']
            )
        )
    
    if 'group_message_id' in message_data:
        delete_tasks.append(
            context.bot.delete_message(
                chat_id=GROUP_ID,
                message_id=message_data['group_message_id']
            )
        )

    # Запускаем все задачи удаления параллельно
    results = await asyncio.gather(*delete_tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            print(f"Ошибка удаления сообщения: {result}")

    # Открепление сообщения
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()

    sender = next((u for u in context.bot_data['users_data'] 
                  if str(u['код']) == context.user_data.get('code')), None)
    
    if sender and 'group_message_id' in message_data:
        try:
            await context.bot.unpin_chat_message(
                chat_id=sender['id'],
                message_id=message_data['group_message_id']
            )
            print(f"[DEBUG] Сообщение {message_data['group_message_id']} откреплено.")
        except Exception as e:
            print(f"Ошибка открепления сообщения: {e}")

    # Обновление интерфейса
    try:
        await query.edit_message_text("✅ Проблема отмечена как решенная. Сообщения удалены и откреплены.")
    except Exception as e:
        print(f"Ошибка редактирования сообщения: {e}")

    # Очистка данных
    context.user_data.pop(unique_id, None)
