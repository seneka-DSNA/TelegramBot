# middleware.py
from functools import wraps


def require_session(handler):
    """
    Middleware que exige una sesión válida en chat privado.
    """

    @wraps(handler)
    async def wrapper(update, context, *args, **kwargs):
        chat = update.effective_chat

        # Solo permitimos chat privado
        if chat.type != "private":
            return

        session_manager = context.application.bot_data.get("session_manager")
        if not session_manager:
            # Error de configuración del bot
            await context.bot.send_message(
                chat_id=chat.id,
                text="Error interno. Inténtalo más tarde."
            )
            return

        session = session_manager.get(chat.id)
        if not session:
            return

        # Inyectamos la sesión en el contexto para el handler
        context.session = session

        return await handler(update, context, *args, **kwargs)

    return wrapper

