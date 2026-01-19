
import sqlite3
from datetime import datetime, timezone
from db import get_connection


class OrderMessageRepository:

    def insert(self, order_id: int, sender: str, message: str):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO order_messages (order_id, sender, message, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    order_id,
                    sender,
                    message,
                    datetime.now(timezone.utc).isoformat(),
                )
            )
            conn.commit()
        finally:
            conn.close()

