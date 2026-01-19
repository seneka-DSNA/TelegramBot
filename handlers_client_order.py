from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from middleware import require_session
from order import Order
from order_state import OrderState
from product_repository import list_active_products
from order_repository import insert_order, cancel_order_by_client
from messaging_service import MessagingService
from group_order_builder import GroupOrderMessageBuilder
from product_repository import list_active_products
# -------------------------------------------------
# UI helpers
# -------------------------------------------------

def build_products_keyboard(products, order: Order):
    keyboard = []

    for p in products:
        qty = order.products.get(p["id"], 0)
        counter = f"x{qty}"

        # Fila 1: nombre del producto
        keyboard.append([
            InlineKeyboardButton(f"🧾 {p['name']}", callback_data="IGNORE")
        ])

        # Fila 2: controles
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"ORDER_DEC_{p['id']}"),
            InlineKeyboardButton(counter, callback_data="IGNORE"),
            InlineKeyboardButton("➕", callback_data=f"ORDER_INC_{p['id']}"),
        ])

    keyboard.append([
        InlineKeyboardButton("✅ Continuar", callback_data="ORDER_NEXT")
    ])

    return InlineKeyboardMarkup(keyboard)


# -------------------------------------------------
# START ORDER
# -------------------------------------------------

@require_session
async def client_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = list_active_products()

    if not products:
        await update.callback_query.edit_message_text(
            "❌ No hay productos disponibles."
        )
        return

    order = Order()
    context.user_data.clear()
    context.user_data["order"] = order
    context.user_data["state"] = OrderState.SELECT_PRODUCT

    keyboard = build_products_keyboard(products, order)

    await update.callback_query.edit_message_text(
        "🛒 Selecciona productos:",
        reply_markup=keyboard
    )


# -------------------------------------------------
# PRODUCT SELECTION CALLBACKS
# -------------------------------------------------

@require_session
async def client_order_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    state = context.user_data.get("state")
    order: Order = context.user_data.get("order")

    if state != OrderState.SELECT_PRODUCT or not order:
        return

    products = list_active_products()

    if data.startswith("ORDER_INC_"):
        order.add_product(int(data.replace("ORDER_INC_", "")))

    elif data.startswith("ORDER_DEC_"):
        order.remove_product(int(data.replace("ORDER_DEC_", "")))

    elif data == "ORDER_NEXT":
        if not order.has_products():
            await query.answer("Selecciona al menos un producto", show_alert=True)
            return

        context.user_data["state"] = OrderState.ADDRESS
        await query.edit_message_text("📍 Introduce la dirección de entrega:")
        return

    keyboard = build_products_keyboard(products, order)
    await query.edit_message_reply_markup(reply_markup=keyboard)


# -------------------------------------------------
# TEXT FLOW HANDLER
# -------------------------------------------------

async def client_order_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    state: OrderState = context.user_data.get("state")
    order: Order = context.user_data.get("order")

    if not state or not order:
        return

    # ADDRESS
    if state == OrderState.ADDRESS:
        order.set_address(text)
        context.user_data["state"] = OrderState.MESSAGE

        await update.message.reply_text(
            "✍️ Mensaje para el repartidor (opcional, escribe '-' si no quieres):"
        )
        return

    # MESSAGE
    if state == OrderState.MESSAGE:
        order.set_message("" if text == "-" else text)
        context.user_data["state"] = OrderState.TIME

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Lo antes posible", callback_data="TIME_ASAP")],
            [
                InlineKeyboardButton("⏱ 1h", callback_data="TIME_1H"),
                InlineKeyboardButton("⏱ 2h", callback_data="TIME_2H"),
            ],
            [
                InlineKeyboardButton("⏱ 3h", callback_data="TIME_3H"),
                InlineKeyboardButton("⏱ 4h", callback_data="TIME_4H"),
            ],
        ])

        await update.message.reply_text(
            "⏰ ¿Cuándo debe llegar el pedido?",
            reply_markup=keyboard
        )
        return


# -------------------------------------------------
# TIME SELECTION CALLBACK
# -------------------------------------------------

@require_session
async def client_order_time_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    state = context.user_data.get("state")
    order: Order = context.user_data.get("order")

    if state != OrderState.TIME or not order:
        return

    TIME_MAP = {
        "TIME_ASAP": "Lo antes posible",
        "TIME_1H": "1 hora",
        "TIME_2H": "2 horas",
        "TIME_3H": "3 horas",
        "TIME_4H": "4 horas",
    }

    if data not in TIME_MAP:
        return

    order.set_delivery_time(TIME_MAP[data])
    context.user_data["state"] = OrderState.CONFIRM

    summary = (
        "🧾 *Resumen del pedido*\n\n"
        f"📍 Dirección: {order.address}\n"
        f"✍️ Mensaje: {order.message or '—'}\n"
        f"⏰ Tiempo: {order.delivery_time}\n\n"
        "¿Confirmas el pedido?"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirmar", callback_data="ORDER_CONFIRM"),
            InlineKeyboardButton("❌ Cancelar", callback_data="ORDER_CANCEL"),
        ]
    ])

    await query.edit_message_text(
        summary,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# -------------------------------------------------
# CONFIRM / CANCEL CALLBACK
# -------------------------------------------------

@require_session
async def client_order_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    state = context.user_data.get("state")
    order: Order = context.user_data.get("order")

    if state != OrderState.CONFIRM or not order:
        return

    if data == "ORDER_CANCEL":
        context.user_data.clear()
        await query.edit_message_text("❌ Pedido cancelado.")
        return

    if data == "ORDER_CONFIRM":
        if not order.is_complete():
            await query.answer("Pedido incompleto.", show_alert=True)
            return
        client_chat_id = update.effective_chat.id
        order.client_chat_id = client_chat_id

        order_id = insert_order(
            client_chat_id=order.client_chat_id,
            client_id=context.session.client_id,
            address=order.address,
            message=order.message,
            delivery_time=order.delivery_time,
            products=order.products,
        )
        products = list_active_products()
       
        product_names = {
            product["id"]: product["name"]
            for product in products
        }
 
        messaging_service = MessagingService(context.bot)
        text, keyboard = GroupOrderMessageBuilder.build(order_id, order=order, product_names=product_names)
        await messaging_service.send_to_group(
            text=text,
            reply_markup= keyboard
        )

        context.user_data.clear()
        await query.edit_message_text(
            "✅ Pedido confirmado. En breve será preparado."
        )
@require_session
async def client_order_cancel_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    order_id = int(data.split("_")[-1])

    # Persistir cancelación
    cancel_order_by_client(order_id)

    # Bloquear interacción del cliente
    session = context.session
    session.disable_reply()

    # Notificar al grupo
    messaging_service = MessagingService(context.bot)
    await messaging_service.send_to_group(
        text=f"❌ Pedido {order_id} cancelado por el cliente."
    )

    # Feedback al cliente
    await query.edit_message_text(
        "❌ Has cancelado el pedido. Si necesitas algo más, puedes iniciar uno nuevo."
    )

