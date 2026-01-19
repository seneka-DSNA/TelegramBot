# services/group_conversation_service.py

from order_repository import get_client_chat_id
from order_message_repository import OrderMessageRepository
from messaging_service import MessagingService
from builder_client_menu import build_client_menu

class GroupConversationService:

    def __init__(self, bot, session_manager):
        self.messaging = MessagingService(bot)
        self.message_repo = OrderMessageRepository()
        self.session_manager = session_manager
    async def send_message_to_client(self, order_id: int, text: str):
        client_chat_id = get_client_chat_id(order_id)

        if not client_chat_id:
            raise ValueError("Client chat_id not found for order")

        # Guardar mensaje
        self.message_repo.insert(
            order_id=order_id,
            sender="COURIER",
            message=text
        )

        # Enviar al cliente
        await self.messaging.send_to_user(
            chat_id=client_chat_id,
            text=(
                f"📩 Mensaje del repartidor "
                f"(Pedido #{order_id}):\n\n{text}"
            )
        )
       
        session = self.session_manager.get(client_chat_id)

        if session:
            session.enable_reply(order_id)

        await self.messaging.send_to_user(
            chat_id=client_chat_id,
            text="💬 Tienes un nuevo mensaje del repartidor. Puedes responder desde el menú.",
            reply_markup=build_client_menu(session)
)
