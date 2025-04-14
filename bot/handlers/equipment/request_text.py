from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import asyncio


async def handle_equipment_input(update: Update, context: CallbackContext) -> int:
    equipment_request = update.message.text
    context.user_data['equipment_request'] = equipment_request

    # Кэширование данных пользователей
    if 'users_data' not in context.bot_data:
        context.bot_data['users_data'] = await load_users_data_async()  # Ваша асинхронная функция загрузки

    users_data = context.bot_data['users_data']
    
    # Поиск отправителя
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        await update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Асинхронная отправка в канал
    channel_data = await send_plea_to_channel_async(context, equipment_request, 
                                                  sender['имя'], sender['фамилия'], 
                                                  sender['статус'], 'equipment_request')

    if not channel_data.get('channel_message_id') or not channel_data.get('thread_id'):
        await update.message.reply_text("❌ Ошибка: не удалось получить ID сообщения или треда.")
        return ConversationHandler.END

    thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{channel_data['channel_message_id']}?thread={channel_data['thread_id']}"

    # Получаем технозондеров (предварительно кэшировано)
    tech_zonders = [user['id'] for user in users_data if user.get('технозондер') == '1']

    if not tech_zonders:
        await update.message.reply_text("❌ Нет технозондеров для рассылки!")
    else:
        formatted_message = (
            f"📢 ЗАПРОС ТЕХНИКИ 📢\n\n"
            f"{equipment_request}\n\n"
            f"С уважением,\n"
            f"{sender['имя']} {sender['фамилия']}"
        )

        keyboard = [[InlineKeyboardButton("Подставить техноплечо 🦾", url=thread_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Асинхронная массовая отправка
        send_tasks = [
            context.bot.send_message(
                chat_id=user_id,
                text=formatted_message,
                reply_markup=reply_markup
            )
            for user_id in tech_zonders
        ]
        
        # Обработка ошибок при отправке
        results = await asyncio.gather(*send_tasks, return_exceptions=True)
        for user_id, result in zip(tech_zonders, results):
            if isinstance(result, Exception):
                print(f"Ошибка отправки {user_id}: {result}")

        await update.message.reply_text(f"✅ Запрос отправлен {len(tech_zonders)} технозондерам!")

    return await show_staff_menu(update, context)
