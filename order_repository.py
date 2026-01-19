import sqlite3
from contextlib import closing
from db import get_connection
from typing import Optional


def insert_order(
    client_id: str,
    address: str,
    message: str,
    delivery_time: str,
    client_chat_id: int,
    products: dict[int, int],
):
    """
    Persists an order and its items in a single transaction.
    """

    if not products:
        raise ValueError("Order must contain at least one product")

    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        try:
            # Insert order
            cursor.execute(
                """
                INSERT INTO orders (client_id, address, message, delivery_time, client_chat_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (client_id, address, message, delivery_time, client_chat_id),
            )

            order_id = cursor.lastrowid

            # Insert order items
            for product_id, quantity in products.items():
                cursor.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, quantity)
                    VALUES (?, ?, ?)
                    """,
                    (order_id, product_id, quantity),
                )

            conn.commit()
            return order_id
            
        except Exception:
                conn.rollback()
                raise
        finally: 
            conn.close()

def get_client_chat_id(order_id: int) -> Optional[int]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT client_chat_id FROM orders WHERE id = ?",
            (order_id,)
        )
        row = cur.fetchone()
        return row["client_chat_id"] if row else None
    finally:
        conn.close()

def cancel_order_by_producer(order_id: int):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE orders
            SET status = 'CANCELLED_BY_PRODUCER'
            WHERE id = ?
            """,
            (order_id,)
        )
        conn.commit()

def cancel_order_by_client(order_id: int):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE orders
            SET status = 'CANCELLED_BY_CLIENT'
            WHERE id = ?
            """,
            (order_id,)
        )
        conn.commit()

