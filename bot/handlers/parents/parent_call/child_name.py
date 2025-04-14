from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from fuzzywuzzy import process  # для fuzzy-поиска
import asyncio  # для асинхронной версии


async def handle_child_name_input(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    
    if len(parts := user_input.split()) < 2:
        await update.message.reply_text("❌ Пожалуйста, введите имя и фамилию ребенка.")
        return INPUT_CHILD_NAME

    # Проверка и кэширование данных
    if 'kids_data' not in context.user_data:
        await update.message.reply_text("⚠️ Ошибка: данные школьников не загружены.")
        return ConversationHandler.END
        
    kids_data = context.user_data['kids_data']

    # Оптимизированный поиск
    search_list = [f"{kid['фамилия']} {kid['имя']}" for kid in kids_data]
    
    # Сначала проверяем точные совпадения
    exact_matches = [
        kid for kid in kids_data 
        if user_input.lower() == f"{kid['фамилия']} {kid['имя']}".lower()
    ]
    
    if not exact_matches:
        # Только если нет точных совпадений - fuzzy search
        matches = process.extract(user_input, search_list, limit=5)
        matched_children = [
            kid for kid in kids_data
            if f"{kid['фамилия']} {kid['имя']}" in [m[0] for m in matches if m[1] >= 70]
        ]
    else:
        matched_children = exact_matches

    if not matched_children:
        await update.message.reply_text("❌ Не удалось найти ребенка. Попробуйте еще раз.")
        return INPUT_CHILD_NAME

    # Обработка результатов
    if len(matched_children) == 1:
        context.user_data['selected_child'] = matched_children[0]
        await update.message.reply_text(
            f"✅ Вы выбрали:\n{matched_children[0]['имя']} {matched_children[0]['фамилия']} "
            f"({matched_children[0]['команда']})\n\n"
            "Это сообщение будет направлено вожатым. Напишите, что нужно передать:"
        )
        return INPUT_MESSAGE_FOR_CHILD

    # Создание клавиатуры
    buttons = [
        InlineKeyboardButton(
            f"{child['фамилия']} {child['имя']} {child.get('отчество', '')} ({child['команда']})",
            callback_data=f"select_child_{idx}"
        )
        for idx, child in enumerate(matched_children)
    ]
    
    await update.message.reply_text(
        "Найдено несколько детей. Выберите нужного:",
        reply_markup=InlineKeyboardMarkup([buttons[i:i+1] for i in range(len(buttons))])
    )
    
    context.user_data['matched_children'] = matched_children
    return CHOOSE_CHILD
