from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from fuzzywuzzy import process

from your_google_sheet_module import async_read_google_sheet_sheet2


async def handle_student_info_input(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    
    if len(parts := user_input.split()) < 2:
        await update.message.reply_text("❌ Пожалуйста, введите имя и фамилию школьника.")
        return INPUT_STUDENT_INFO

    # Используем кэшированные данные
    if 'parents_data' not in context.bot_data:
        try:
            context.bot_data['parents_data'] = await async_read_google_sheet_sheet2(TABULA_kids)
            context.bot_data['search_list'] = [
                f"{p['фамилия']} {p['имя']}" for p in context.bot_data['parents_data']
            ]
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            await update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
            return ConversationHandler.END

    # Быстрый поиск точных совпадений перед fuzzy
    exact_matches = [
        p for p in context.bot_data['parents_data']
        if user_input.lower() in f"{p['фамилия']} {p['имя']}".lower()
    ]
    
    if not exact_matches:
        # Fuzzy search только если нет точных совпадений
        matches = process.extract(user_input, context.bot_data['search_list'], limit=5)
        matched_parents = [
            p for p in context.bot_data['parents_data']
            if f"{p['фамилия']} {p['имя']}" in [m[0] for m in matches if m[1] >= 70]
        ]
    else:
        matched_parents = exact_matches

    if not matched_parents:
        await update.message.reply_text("❌ Не удалось найти школьника. Попробуйте еще раз.")
        return INPUT_STUDENT_INFO

    if len(matched_parents) == 1:
        context.user_data['selected_student'] = matched_parents[0]
        await update.message.reply_text(
            f"✅ Наряд получит:\n\n"
            f"{matched_parents[0]['фамилия']} {matched_parents[0]['имя']} ({matched_parents[0]['команда']})"
        )
        await update.message.reply_text("Укажите причину наряда:")
        return INPUT_DUTY_TEXT

    # Оптимизированное создание клавиатуры
    buttons = [
        InlineKeyboardButton(
            f"{p['фамилия']} {p['имя']} {p.get('отчество', '')} ({p['команда']})",
            callback_data=f"select_student_{idx}"
        )
        for idx, p in enumerate(matched_parents)
    ]
    await update.message.reply_text(
        "Найдено несколько школьников. Выберите нужного:",
        reply_markup=InlineKeyboardMarkup([buttons[i:i+1] for i in range(len(buttons))])
    )

    context.user_data['matched_students'] = matched_parents
    return CHOOSE_STUDENT
