from telegram import Update
from telegram.ext import ContextTypes
from middleware import require_session


@require_session
async def client_incoming_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = context.session

    text = update.message.text
    if "(Pedido #" not in text:
        return

    try:
        order_id = int(text.split("(Pedido #")[1].split(")")[0])
    except Exception:
        return

    session.enable_reply(order_id)

    await update.message.reply_text(
        "💬 Puedes responder al repartidor desde el menú."
    )

