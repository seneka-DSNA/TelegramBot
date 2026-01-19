from order_message_repository import OrderMessageRepository
from messaging_service import MessagingService
from config import PRODUCER_GROUP_ID


class ClientConversationService:

    def __init__(self, bot):
        self.messaging = MessagingService(bot)
        self.message_repo = OrderMessageRepository()

    async def send_message_to_group(self, order_id: int, text: str):
        self.message_repo.insert(
            order_id=order_id,
            sender="CLIENT",
            message=text
        )

        await self.messaging.send_to_group(
            text=(
                f"📩 Cliente (Pedido #{order_id}):\n\n{text}"
            )
        )
    async def notify_group_order_closed(self, order_id: int):
        # Persistimos el evento (opcional pero recomendable)
        self.message_repo.insert(
            order_id=order_id,
            sender="SYSTEM",
            message="Pedido cerrado por el cliente",
        )

        # Notificamos al grupo
        await self.messaging.send_to_group(
            text=(
                f"❌ *Pedido #{order_id} cerrado por el cliente.*\n\n"
                "La conversación ha finalizado."
            ),
            parse_mode="Markdown",
        )
