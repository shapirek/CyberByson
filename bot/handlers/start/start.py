from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

# Функция обработки команды /start. Отправляем приветственное сообщение и показываем главное меню.
def start(update: Update, context: CallbackContext) -> int:
    # Сбрасываем все данные пользователя
    context.user_data.clear()

    # Отправляем приветственное сообщение и показываем главное меню
    update.message.reply_text("Вас приветствует КиберБизон!\n Этот бот предназначен помочь упростить некоторые процессы в КЛШ.\n Если что-то пошло не так, рекомендуем "перезагрузить" бота — написать команду /start.")
    show_main_menu(update, context)

    return ConversationHandler.END  # Сбрасываем состояние
