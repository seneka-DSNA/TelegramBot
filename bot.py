# bot.py
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ========================
# CONFIG
# ========================
BOT_TOKEN = 


# ========================
# SERVICES / CORE
# ========================
from session_manager import SessionManager
from auth_service import AuthService
from client_repository import ClientRepository
from access_code_repository import AccessCodeRepository

# ========================
# HANDLERS – AUTH / MENU
# ========================
from handlers_auth import start_handler, auth_handler
from handlers_menu import menu_handler, menu_text_handler
from handlers_entry import private_entry_handler
# ========================
# HANDLERS – CLIENT ORDER
# ========================
from handlers_client_order import (
    client_order_start,
    client_order_product_callback,
    client_order_confirm_callback,
    client_order_time_callback,
    client_order_text_handler,
    client_order_cancel_callback
)

# ========================
# HANDLERS – CLIENT ↔ GROUP MESSAGING
# ========================
from handlers_client_message import client_incoming_message_handler
from handlers_client import (
    client_reply_start_handler,
    client_reply_message_handler,
    client_close_order_handler,
)
from handlers_client_catalog import client_catalog_handler
# ========================
# HANDLERS – GROUP
# ========================
from handlers_group import group_callback_handler, group_cancel_order_handler
from handlers_group_message import group_text_message_handler


# ========================
# ERROR HANDLER
# ========================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print("ERROR:", context.error)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ========================
    # SHARED SERVICES
    # ========================
    session_manager = SessionManager(ttl_seconds=1800)
    auth_service = AuthService(
        ClientRepository(),
        AccessCodeRepository(),
    )

    app.bot_data["session_manager"] = session_manager
    app.bot_data["auth_service"] = auth_service

    # ============================================================
    # COMMANDS
    # ============================================================
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("menu", menu_handler))

    # ============================================================
    # GROUP 1 — SYSTEM / HIGH PRIORITY (PRIVATE)
    # ============================================================
    # Mensajes entrantes del repartidor → cliente
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.TEXT,
            client_incoming_message_handler,
        ),
        group=1,
    )

    # ============================================================
    # GROUP 2 — CLIENT REPLY FLOW
    # ============================================================
    app.add_handler(
        CallbackQueryHandler(
            client_reply_start_handler,
            pattern=r"^CLIENT_REPLY$",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            client_close_order_handler,
            pattern="^CLIENT_CLOSE_ORDER$",
        )
    )
   
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.TEXT,
            client_reply_message_handler,
        ),
        group=2,
    )

    # ============================================================
    # GROUP 0 — AUTH
    # ============================================================
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.Regex(r"(?i)^menu$"),
            menu_text_handler,
        ),
        group=0,
    )
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.TEXT,
            auth_handler,
        ),
        group=0,
    )

    # ============================================================
    # GROUP 3 — CLIENT ORDER FLOW
    # ============================================================
    app.add_handler(
        CallbackQueryHandler(
            client_order_start,
            pattern=r"^CLIENT_ORDER$",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            client_catalog_handler,
            pattern="^CATALOGO$",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            client_order_product_callback,
            pattern=r"^ORDER_(INC|DEC|NEXT)|^ORDER_NEXT$",
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            client_order_confirm_callback,
            pattern=r"^ORDER_(CONFIRM|CANCEL)$",
        )
    )
   
    app.add_handler(
        CallbackQueryHandler(
            client_order_cancel_callback,
            pattern=r"^CLIENT_CANCEL_ORDER_"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            client_order_time_callback,
            pattern=r"^TIME_",
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            client_order_text_handler,
        ),
        group=3,
    )

    # ============================================================
    # GROUP 4 — GROUP (PRODUCERS)
    # ============================================================
    app.add_handler(
        CallbackQueryHandler(
            group_callback_handler,
            pattern=r"^GROUP_MSG_",
        )
    )

    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & filters.TEXT,
            group_text_message_handler,
        )
    )
    
    app.add_handler(
        CallbackQueryHandler(
            group_cancel_order_handler,
            pattern=r"^ORDER_CANCEL_BY_PRODUCER_"
        )
    )

    # ============================================================
    # ERROR HANDLER
    # ============================================================
    app.add_error_handler(error_handler)

    # ============================================================
    # START BOT
    # ============================================================
    app.run_polling()


if __name__ == "__main__":
    main()

