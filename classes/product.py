import psycopg2
from psycopg2 import pool

# 🔥 Connection pool (reuses connections instead of spamming new ones)
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,
    "postgresql://postgres.ltwkdwxckpewhmtpjpvj:oCD4aNWbC7dd7MYG@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)

class Product:
    def __init__(self, id=None, name=None, price=None, stock=None, picture=None):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.image_url = picture

    def get_products(self):
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("SELECT * FROM products")
            rows = cur.fetchall()
            return [Product(*row) for row in rows]

        finally:
            cur.close()
            release_connection(conn)

    def get_product_by_id(self, product_id):
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            row = cur.fetchone()

            if row:
                return Product(*row)
            return None

        finally:
            cur.close()
            release_connection(conn)