# handlers_auth.py

from telegram import Update
from telegram.ext import ContextTypes

from auth_hooks import on_login_success

AUTH_PASSWORD = "auth_password"
AUTH_WAITING_CODE = "auth_waiting_code"


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start – punto de entrada del bot
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    client_id = str(user.id)

    session_manager = context.application.bot_data["session_manager"]

    # Si ya hay sesión, ir directamente al menú
    if session_manager.get(chat_id):
        await update.message.reply_text("✅ Ya estás autenticado.")
        await on_login_success(update, context)
        return

    # Iniciar flujo de autenticación
    context.user_data.clear()
    context.user_data["client_id"] = client_id
    context.user_data["state"] = AUTH_PASSWORD

    await update.message.reply_text("🔐 Introduce tu contraseña:")


async def auth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_manager = context.application.bot_data["session_manager"]
    chat_id = update.effective_chat.id

    if session_manager.get(chat_id):
        return

    text = update.message.text.strip()
    state = context.user_data.get("state", AUTH_PASSWORD)

    auth_service = context.application.bot_data["auth_service"]
    client_id = context.user_data.get("client_id")

    # --------------------------------------------------
    # Paso 1: password
    # --------------------------------------------------
    if state == AUTH_PASSWORD:
        context.user_data["password"] = text

        result = auth_service.authenticate(
            client_id=client_id,
            password=text,
        )

        # Login correcto (usuario existente)
        if result.success:
            session_manager.create(
                chat_id=chat_id,
                client_id=client_id,
            )
            context.user_data.clear()
            await update.message.reply_text("✅ Autenticación correcta.")
            await on_login_success(update, context)
            return

        # Requiere access_code (usuario nuevo)
        if "access code" in result.message.lower():
            context.user_data["state"] = AUTH_WAITING_CODE
            await update.message.reply_text("🔑 Introduce tu access_code:")
            return

        # Error fatal
        context.user_data.clear()
        await update.message.reply_text(f"❌ {result.message}")
        return

    # --------------------------------------------------
    # Paso 2: access_code (registro)
    # --------------------------------------------------
    if state == AUTH_WAITING_CODE:
        access_code = text
        password = context.user_data.get("password")

        result = auth_service.authenticate(
            client_id=client_id,
            password=password,
            access_code=access_code,
        )

        if result.success:
            session_manager.create(
                chat_id=chat_id,
                client_id=client_id,
            )
            context.user_data.clear()
            await update.message.reply_text("✅ Registro y autenticación correctos.")
            await on_login_success(update, context)
            return

        context.user_data.clear()
        await update.message.reply_text(f"❌ {result.message}")
        return

