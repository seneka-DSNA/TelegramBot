from telegram import Update
from telegram.ext import ContextTypes
from handlers_auth import start_handler, auth_handler
from handlers_menu import menu_handler


async def private_entry_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat or chat.type != "private":
        return
    if context.user_data.get("state"):
        return
    session_manager = context.application.bot_data["session_manager"]
    session = session_manager.get(chat.id)

    if session:
        # Usuario autenticado → menú
        await menu_handler(update, context)
        return
    if "client_id" not in context.user_data:
        await start_handler(update, context)
        return
    
    await auth_handler(update, context)
