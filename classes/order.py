import psycopg2
from flask import session
from classes.product import Product
from classes.cart import Cart
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    1, 10,
    "postgresql://postgres.ltwkdwxckpewhmtpjpvj:oCD4aNWbC7dd7MYG@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)

class Order:

    def place_order(self):
        if "user_id" not in session:
            return False, "User not logged in"

        user_id = session["user_id"]
        cart = Cart()

        if not cart.items:
            return False, "Cart is empty"

        conn = get_connection()
        cur = conn.cursor()

        try:
            # 🔥 Get ALL products once (no loop DB calls)
            p = Product()
            all_products = p.get_products()
            product_dict = {prod.id: prod for prod in all_products}

            # 🔥 Calculate total safely
            total_price = 0
            for product_id, qty in cart.items.items():
                product = product_dict.get(int(product_id))
                if product:
                    total_price += product.price * qty

            # 🔥 Create order
            cur.execute(
                "INSERT INTO orders (user_id, status, total_price) VALUES (%s, %s, %s) RETURNING id",
                (user_id, "placed", total_price)
            )
            order_id = cur.fetchone()[0]

            # 🔥 Insert order items
            for product_id, qty in cart.items.items():
                product = product_dict.get(int(product_id))

                if not product:
                    continue

                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                    (order_id, int(product_id), qty, product.price)
                )

            # 🔥 Clear cart
            cart.items = {}
            cart.save()

            conn.commit()

            return True, order_id

        except Exception as e:
            conn.rollback()
            return False, str(e)

        finally:
            cur.close()
            release_connection(conn)
    
    def get_orders_by_user(self, user_id):
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT id, created_at, status, total_price
                FROM orders
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))

            orders = cur.fetchall()
            result = []

            for order in orders:
                order_id = order[0]

                cur.execute("""
                    SELECT product_id, quantity, price
                    FROM order_items
                    WHERE order_id = %s
                """, (order_id,))

                items = cur.fetchall()

                result.append({
                    "id": order[0],
                    "created_at": order[1],
                    "status": order[2],
                    "total": order[3],
                    "items": items
                })

            return result

        finally:
            cur.close()
            release_connection(conn)