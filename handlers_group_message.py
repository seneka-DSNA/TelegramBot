
from telegram import Update
from telegram.ext import ContextTypes

from group_conversation_service import GroupConversationService


async def group_text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data

    if "replying_to_order" not in chat_data:
        return

    order_id = chat_data["replying_to_order"]
    text = update.message.text
    session_manager = context.application.bot_data["session_manager"]
    service = GroupConversationService(context.bot, session_manager)

    try:
        await service.send_message_to_client(order_id, text)
        await update.message.reply_text("📨 Mensaje enviado al cliente.")
    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Error enviando el mensaje.")

    # Limpiar estado
    chat_data.pop("replying_to_order", None)

