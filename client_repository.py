from db import get_connection


class ClientRepository:
    def get_by_client_id(self, client_id: str):
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM clients WHERE client_id = ?",
                (client_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def increment_failed_attempts(self, client_id: str):
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE clients
                SET failed_attempts = failed_attempts + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE client_id = ?
                """,
                (client_id,)
            )
            conn.commit()

    def reset_failed_attempts(self, client_id: str):
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE clients
                SET failed_attempts = 0,
                    updated_at = CURRENT_TIMESTAMP
                WHERE client_id = ?
                """,
                (client_id,)
            )
            conn.commit()

    def update_status(self, client_id: str, status: str):
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE clients
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE client_id = ?
                """,
                (status, client_id)
            )
            conn.commit()
    def create(self, client_id: str, password_hash: str, status: str):
        """
        Crea un nuevo cliente en la base de datos.
        Se asume que el client_id no existe previamente.
        """
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO clients (
                    client_id,
                    password_hash,
                    status,
                    failed_attempts,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (client_id, password_hash, status)
            )
            conn.commit()
