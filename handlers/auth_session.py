from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ---------- UI ----------

def auth_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Autenticar", callback_data="AUTH_START")]
    ])


# ---------- Handlers ----------

async def start_auth(update, context):
    query = update.callback_query
    await query.answer()

    context.chat_data["awaiting_auth_code"] = True

    await query.edit_message_text(
        "🔐 Introduce tu código de acceso:"
    )


async def receive_auth_code(update, context):
    chat = update.effective_chat
    code = update.message.text.strip()

    if not context.chat_data.get("awaiting_auth_code"):
        return

    auth_service = context.application.bot_data["auth_service"]

    if auth_service.authenticate(chat.id, code):
        context.chat_data.pop("awaiting_auth_code", None)

        await update.message.reply_text(
            "✅ Autenticación correcta."
        )
    else:
        await update.message.reply_text(
            "❌ Código incorrecto. Inténtalo de nuevo."
        )
