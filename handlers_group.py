# handlers/group_handlers.py

from telegram import Update
from telegram.ext import ContextTypes

from group_conversation_service import GroupConversationService
from order_repository import get_client_chat_id, cancel_order_by_producer

async def group_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if not data.startswith("GROUP_MSG_"):
        return

    order_id = int(data.split("_")[-1])

    # Guardamos estado del grupo
    context.chat_data["replying_to_order"] = order_id

    await query.message.reply_text(
        f"✏️ Escribe el mensaje para el cliente del pedido #{order_id}"
    )

async def group_close_order_handler(update, context):
    query = update.callback_query
    await query.answer()

    order_id = extract_order_id(query.data)

    session_manager = context.application.bot_data["session_manager"]
    client_chat_id = get_client_chat_id(order_id)

    session = session_manager.get(client_chat_id)
    if session:
        session.disable_reply()

    await query.edit_message_text("✅ Pedido cerrado por el repartidor.")

async def group_cancel_order_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    order_id = int(data.split("_")[-1])

    # Persistencia
    cancel_order_by_producer(order_id)  # o delete_order()

    # Bloquear cliente
    client_chat_id = get_client_chat_id(order_id)
    session = context.application.bot_data["session_manager"].get(client_chat_id)
    if session:
        session.disable_reply()

    # Notificar cliente
    await context.bot.send_message(
        chat_id=client_chat_id,
        text="❌ Tu pedido ha sido cancelado por el repartidor."
    )

    # Actualizar grupo
    await query.edit_message_text(
        "❌ Pedido cancelado por el repartidor."
    )

