import psycopg2

# Connect to PostgreSQL
con = psycopg2.connect(
    "postgresql://postgres.ltwkdwxckpewhmtpjpvj:oCD4aNWbC7dd7MYG@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
)
cur = con.cursor()

class Product:
    def __init__(self, id=None, name=None, price=None, stock=None, picture=None):
        # For database methods, we allow empty constructor
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.picture = picture

    def is_in_stock(self):
        return self.stock > 0

    def reduce_stock(self, qty):
        if qty <= self.stock:
            self.stock -= qty
        else:
            print("Not enough in stock")

    def increase_stock(self, qty):
        if qty > 0:
            self.stock += qty

    # Instance method to fetch all products
    def get_products(self):
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()
        return rows

    # Instance method to fetch product by id
    def get_product_by_id(self, product_id):
        cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        row = cur.fetchone()
        if row:
            return Product(*row)
        return None