# session_manager.py
import time


class Session:
    def __init__(self, chat_id: int, client_id: str, ttl_seconds: int):
        self.chat_id = chat_id
        self.client_id = client_id
        self.expires_at = time.time() + ttl_seconds
        self.can_reply: bool = False
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def enable_reply(self, order_id: int):
        self.active_order_id = order_id
        self.can_reply = True
     
    def disable_reply(self):
        self.active_order_id = None
        self.can_reply = False


class SessionManager:
    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[int, Session] = {}

    def create(self, chat_id: int, client_id: str) -> None:
        """
        Crea o reemplaza una sesión para un chat_id.
        """
        self._sessions[chat_id] = Session(
            chat_id=chat_id,
            client_id=client_id,
            ttl_seconds=self.ttl_seconds,
        )

    def get(self, chat_id: int) -> Session | None:
        """
        Devuelve la sesión activa o None si no existe o está expirada.
        """
        session = self._sessions.get(chat_id)

        if not session:
            return None

        if session.is_expired():
            self.delete(chat_id)
            return None

        return session

    def delete(self, chat_id: int) -> None:
        """
        Elimina una sesión.
        """
        self._sessions.pop(chat_id, None)

    def clear_expired(self) -> None:
        """
        Limpia todas las sesiones expiradas.
        """
        expired = [
            chat_id
            for chat_id, session in self._sessions.items()
            if session.is_expired()
        ]

        for chat_id in expired:
            self.delete(chat_id)
