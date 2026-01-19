# handlers_client.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ROLE_CLIENT
from middleware import require_session
from client_conversation_service import ClientConversationService
SESSION_TTL_MINUTES = 30  # X tiempo


@require_session
async def client_reply_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    session = context.session

    if not session.can_reply or not session.active_order_id:
        await query.edit_message_text("❌ No hay mensajes a los que responder.")
        return

    context.user_data["state"] = "CLIENT_REPLYING"

    await query.edit_message_text(
        "✏️ Escribe tu mensaje para el repartidor."
    )


@require_session
async def client_reply_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "CLIENT_REPLYING":
        return

    session = context.session
    order_id = session.active_order_id
    text = update.message.text

    service = ClientConversationService(context.bot)

    await service.send_message_to_group(order_id, text)

    context.user_data.clear()

    await update.message.reply_text("📨 Mensaje enviado al repartidor.")

@require_session
async def client_close_order_handler(update, context):
    query = update.callback_query
    await query.answer()

    session = context.session
    order_id = session.active_order_id

    if not order_id:
        await query.edit_message_text("❌ No hay pedido activo.")
        return

    # Cerrar conversación
    session.disable_reply()

    # Notificar al grupo
    service = ClientConversationService(context.bot)
    await service.notify_group_order_closed(order_id)
   
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Greacias por tu pedido."    
    )

    await query.edit_message_text("✅ Pedido cerrado. Gracias.")
