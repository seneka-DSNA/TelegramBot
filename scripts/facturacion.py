import sqlite3
import json

from product_repository import list_active_products


DB_PATH = "./db/bot.db"
OUTPUT_FILE = "order_summary.json"
ACTIVE_STATUS = "CREATED"


def aggregate_active_orders():
    # -------------------------------
    # Catálogo de productos
    # -------------------------------
    products = list_active_products()
    product_map = {
        p["id"]: {
            "name": p["name"],
            "price": p["price"]
        }
        for p in products
    }

    # -------------------------------
    # BD
    # -------------------------------
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            oi.product_id,
            SUM(oi.quantity) AS total_quantity
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE o.status = ?
        GROUP BY oi.product_id
    """, (ACTIVE_STATUS,))

    rows = cursor.fetchall()
    conn.close()

    # -------------------------------
    # Resultado
    # -------------------------------
    result = []

    for product_id, total_quantity in rows:
        product = product_map.get(product_id)
        if not product:
            continue

        unit_price = product["price"]
        total_price = unit_price * total_quantity

        result.append({
            "producto" : product["name"],
            "precio_unidad": unit_price,
            "cantidad": total_quantity,
            "precio_total": total_price,
        })

    # -------------------------------
    # Guardar archivo
    # -------------------------------
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"Resumen generado en {OUTPUT_FILE}")
    print(result)
if __name__ == "__main__":
    aggregate_active_orders()
