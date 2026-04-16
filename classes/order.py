import psycopg2
from flask import session
from classes.product import Product
from classes.cart import Cart


class Order:

    def place_order(self):
        con = psycopg2.connect(
            "postgresql://postgres.ltwkdwxckpewhmtpjpvj:oCD4aNWbC7dd7MYG@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
        )
        # 🔐 Must be logged in
        if "user_id" not in session:
            return False, "User not logged in"

        user_id = session["user_id"]

        cart = Cart()

        if not cart.items:
            return False, "Cart is empty"

        cur = con.cursor()

        # 1. Calculate total
        total_price = cart.total()

        # 2. Create order
        cur.execute(
            "INSERT INTO orders (user_id, status, total_price) VALUES (%s, %s, %s) RETURNING id",
            (user_id, "placed", total_price)
        )

        order_id = cur.fetchone()[0]

        # 3. Add order items
        p = Product()

        for product_id, qty in cart.items.items():
            product = p.get_product_by_id(product_id)

            if not product:
                continue

            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (order_id, product_id, qty, product.price)
            )

            # Optional: reduce stock
            # product.reduce_stock(qty)

        # 4. Clear cart
        cart.items = {}
        cart.save()

        con.commit()
        cur.close()
        con.close()

    def cancel_order(self, order_id):
        if "user_id" not in session:
            return False, "User not logged in"

        user_id = session["user_id"]

        conn = psycopg2.connect(
            "postgresql://postgres.ltwkdwxckpewhmtpjpvj:oCD4aNWbC7dd7MYG@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
        )
        cur = conn.cursor()

        # Check that order belongs to user
        cur.execute("""
                    SELECT status
                    FROM orders
                    WHERE id = %s
                      AND user_id = %s
                    """, (order_id, user_id))

        result = cur.fetchone()

        if not result:
            cur.close()
            conn.close()
            return False, "Order not found"

        current_status = result[0]

        # Prevent cancelling again
        if current_status == "cancelled":
            cur.close()
            conn.close()
            return False, "Order already cancelled"

        # Update status
        cur.execute("""
                    UPDATE orders
                    SET status = %s
                    WHERE id = %s
                    """, ("cancelled", order_id))

        conn.commit()

        cur.close()
        conn.close()

        return True, "Order cancelled"

    
    def get_orders_by_user(self, user_id):
        con = psycopg2.connect(
            "postgresql://postgres.ltwkdwxckpewhmtpjpvj:oCD4aNWbC7dd7MYG@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
        )
        cur = con.cursor()

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

            # Get items for each order
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

        cur.close()
        con.close()
        return result