import os
import logging
import asyncio
import threading
from fastapi import FastAPI
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters
)

from bot.handlers.auth_handlers          import handle_code_input
from bot.handlers.category_handlers      import handle_category
from bot.handlers.inline_handlers        import inline_button_handler
from bot.handlers.news                   import handle_news
from bot.handlers.recipient_handlers     import handle_recipient_choice
from bot.handlers.message_handlers       import handle_input_message
from bot.handlers.response_handlers      import handle_wait_for_response
from bot.handlers.direction_handlers     import handle_direction_choice
from bot.handlers.team_handlers          import handle_team_choice
from bot.handlers.tournament_handlers    import handle_tournament_choice
from bot.handlers.equipment_handlers     import handle_request_equipment, handle_equipment_input
from bot.handlers.duty_handlers          import (
    handle_assign_duty, handle_student_info_input, handle_student_choice, handle_duty_text_input
)
from bot.handlers.parent_handlers        import (
    handle_parent_call, handle_child_name_input, handle_child_choice, handle_message_for_child_input
)
from bot.handlers.problem_handlers       import handle_problem_solved_button

from bot.config import (
    CODE_INPUT, INPUT_MESSAGE, WAIT_FOR_RESPONSE,
    CHOOSE_DIRECTION, CHOOSE_TEAM, CHOOSE_TOURNAMENT,
    REQUEST_EQUIPMENT, INPUT_STUDENT_INFO, INPUT_DUTY_TEXT,
    INPUT_CHILD_NAME, INPUT_MESSAGE_FOR_CHILD,
    DIRECTOR_ACTION, STAFF_ACTION, STUDENTS_ACTION, PARENTS_ACTION,
    CHOOSE_RECIPIENT, CHOOSE_STUDENT, CHOOSE_CHILD
)
from bot.env import TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def health():
    return {"status": "OK"}

async def start_bot():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', handle_category))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_category))
    application.add_handler(CallbackQueryHandler(inline_button_handler))

    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', handle_category),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_category),
            CallbackQueryHandler(inline_button_handler),
        ],
        states={
            CODE_INPUT: [MessageHandler(filters.TEXT, handle_code_input)],
            DIRECTOR_ACTION: [CallbackQueryHandler(inline_button_handler)],
            STAFF_ACTION: [CallbackQueryHandler(inline_button_handler)],
            STUDENTS_ACTION: [CallbackQueryHandler(inline_button_handler)],
            PARENTS_ACTION: [CallbackQueryHandler(inline_button_handler)],
            CHOOSE_RECIPIENT: [CallbackQueryHandler(handle_recipient_choice)],
            INPUT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input_message)],
            WAIT_FOR_RESPONSE: [CallbackQueryHandler(handle_wait_for_response, pattern='^wait_for_response_')],
            CHOOSE_DIRECTION: [CallbackQueryHandler(handle_direction_choice, pattern='^(?!back_to_director).+')],
            CHOOSE_TEAM: [CallbackQueryHandler(handle_team_choice, pattern='^team_|^back_to_message_options$')],
            CHOOSE_TOURNAMENT: [CallbackQueryHandler(handle_tournament_choice, pattern='^tournament_|^back_to_message_options$')],
            REQUEST_EQUIPMENT: [
                CallbackQueryHandler(handle_request_equipment, pattern='^request_equipment$'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_equipment_input)
            ],
            INPUT_STUDENT_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_student_info_input)],
            CHOOSE_STUDENT: [CallbackQueryHandler(handle_student_choice, pattern='^select_student_')],
            INPUT_DUTY_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_duty_text_input)],
            INPUT_CHILD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_child_name_input)],
            CHOOSE_CHILD: [CallbackQueryHandler(handle_child_choice, pattern='^select_child_')],
            INPUT_MESSAGE_FOR_CHILD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_for_child_input)],
        },
        fallbacks=[CommandHandler('start', handle_category)]
    )
    application.add_handler(conv)

    application.add_handler(CallbackQueryHandler(handle_news, pattern='^news$'))
    application.add_handler(CallbackQueryHandler(handle_problem_solved_button, pattern='^problem_solved_'))

    await application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(start_bot()), daemon=True).start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
