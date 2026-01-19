from db import get_connection
from typing import Optional


class AccessCodeRepository:

    def create(self, code: str) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO access_codes (code, used)
                VALUES (?, 0)
                """,
                (code,)
            )
            conn.commit()

    def exists_and_unused(self, code: str) -> bool:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT 1
                FROM access_codes
                WHERE code = ?
                  AND used = 0
                """,
                (code,)
            )
            return cursor.fetchone() is not None

    def mark_as_used(self, code: str, client_id: str) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE access_codes
                SET used = 1,
                    used_by_client_id = ?,
                    used_at = CURRENT_TIMESTAMP
                WHERE code = ?
                """,
                (client_id, code)
            )
            conn.commit()

