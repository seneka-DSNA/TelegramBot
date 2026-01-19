from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from order import Order


class GroupOrderMessageBuilder:

    @staticmethod
    def build(order_id: int, order: Order, product_names: dict[int, str]):
        lines = [
            "📦 NUEVO PEDIDO",
            f"🆔 Pedido #{order_id}",
            "",
            "🛒 Productos:",
        ]

        for product_id, qty in order.products.items():
            name = product_names.get(product_id, f"Producto #{product_id}")
            lines.append(f"• Producto {name} × {qty}")

        lines.extend([
            "",
            f"📍 Dirección:\n{order.address}",
            "",
            f"📝 Mensaje:\n{order.message or '—'}",
            "",
            f"⏰ Entrega: {order.delivery_time}",
        ])

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💬 Escribir al cliente", callback_data=f"GROUP_MSG_{order_id}"),
                InlineKeyboardButton("✅ Marcar entregado", callback_data=f"GROUP_DONE_{order_id}"),
                InlineKeyboardButton("❌ Cancelar pedido", callback_data=f"ORDER_CANCEL_BY_PRODUCER_{order_id}")

            ]
        ])

        return "\n".join(lines), keyboard

