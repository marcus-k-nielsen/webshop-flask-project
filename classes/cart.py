from flask import session
from classes.product import Product
from psycopg2 import pool

# 🔥 Connection pool (shared)
connection_pool = pool.SimpleConnectionPool(
    1, 10,
    "postgresql://postgres.ltwkdwxckpewhmtpjpvj:oCD4aNWbC7dd7MYG@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)


class Cart:
    def __init__(self):
        self.items = session.get("cart", {})  # 🔥 ALWAYS use session

    def save(self):
        session["cart"] = self.items

    def add(self, product_id, qty=1):
        product_id = str(product_id)

        self.items[product_id] = self.items.get(product_id, 0) + qty
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)

        if product_id in self.items:
            del self.items[product_id]

        self.save()

    def update(self, product_id, qty):
        product_id = str(product_id)

        if qty <= 0:
            self.remove(product_id)
        else:
            self.items[product_id] = qty

        self.save()

    def total(self):
        total = 0
        p = Product()

        # 🔥 Fetch ALL products ONCE
        all_products = p.get_products()
        product_dict = {prod.id: prod for prod in all_products}

        for product_id, qty in self.items.items():
            product = product_dict.get(int(product_id))
            if product:
                total += product.price * qty

        return total