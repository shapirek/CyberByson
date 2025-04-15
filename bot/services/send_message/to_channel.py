from telegram.ext import CallbackContext
from telegram import Message


async def send_message_to_channel(context: CallbackContext, message_text: str, sender_name: str, sender_surname: str,
                                  sender_status: str, recipient_type: str, **kwargs) -> None:
    formatted_message = format_message_with_signature(
        message_text, sender_name, sender_surname, sender_status, recipient_type, **kwargs
    )

    try:
        thread_id = context.user_data.get('thread_id')
        reply_to_message_id = thread_id if thread_id else None

        sent_message = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=formatted_message,
            reply_to_message_id=reply_to_message_id
        )

        unique_id = generate_unique_id()

        message_data = {
            'channel_message_id': sent_message.message_id,
            'thread_id': sent_message.message_id,
            'group_message_id': None
        }
        context.user_data[unique_id] = message_data
        context.user_data['current_message_id'] = unique_id

    except Exception as e:
        print(f"Ошибка отправки сообщения в канал: {e}")
