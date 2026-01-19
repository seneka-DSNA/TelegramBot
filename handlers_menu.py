from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from middleware import require_session
from handlers_auth import start_handler


@require_session
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
       [InlineKeyboardButton("📦 Catálogo", callback_data="CATALOGO")],
       [InlineKeyboardButton("🛒 Pedido", callback_data="CLIENT_ORDER")],
   ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            "¿Qué deseas hacer?",
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(
            "¿Qué deseas hacer?",
            reply_markup=reply_markup
        )
async def menu_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Se ejecuta SOLO cuando el usuario escribe 'menu'
    """
    chat = update.effective_chat
    if chat.type != "private":
        return

    session_manager = context.application.bot_data["session_manager"]
    session = session_manager.get(chat.id)

    if session:
        # Usuario autenticado → menú
        await menu_handler(update, context)
    else:
        # Usuario no autenticado → iniciar auth
        await start_handler(update, context)
