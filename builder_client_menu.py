from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_client_menu(session):
    keyboard = [
        [InlineKeyboardButton("🛒 Pedido", callback_data="CLIENT_ORDER")],
    ]

    if session.can_reply and session.active_order_id:
        keyboard.append([
             InlineKeyboardButton("💬 Responder", callback_data="CLIENT_REPLY"),
             InlineKeyboardButton("✅ Cerrar pedido", callback_data="CLIENT_CLOSE_ORDER"),
             InlineKeyboardButton("❌ Cancelar pedido", callback_data=f"CLIENT_CANCEL_ORDER_{session.active_order_id}"),
             
        ])

    return InlineKeyboardMarkup(keyboard)

