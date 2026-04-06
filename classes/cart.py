from flask import session
from classes.product import Product
import psycopg2

con = psycopg2.connect(
    "postgresql://postgres.ltwkdwxckpewhmtpjpvj:oCD4aNWbC7dd7MYG@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
)

class Cart:
    def __init__(self):
        self.items = self.load_cart()

    # ------------------------
    # LOAD CART
    # ------------------------
    def load_cart(self):
        # Logged in → DB
        if "user_id" in session:
            return self.get_cart_from_db(session["user_id"])

        # Guest → session
        return session.get("cart", {})

    # ------------------------
    # SAVE CART
    # ------------------------
    def save(self):
        if "user_id" in session:
            self.save_cart_to_db(session["user_id"])
        else:
            session["cart"] = self.items

    # ------------------------
    # ADD PRODUCT
    # ------------------------
    def add(self, product_id, qty=1):
        product_id = str(product_id)

        if product_id in self.items:
            self.items[product_id] += qty
        else:
            self.items[product_id] = qty

        self.save()

    # ------------------------
    # REMOVE PRODUCT
    # ------------------------
    def remove(self, product_id):
        product_id = str(product_id)

        if product_id in self.items:
            del self.items[product_id]

        self.save()

    # ------------------------
    # UPDATE QUANTITY
    # ------------------------
    def update(self, product_id, qty):
        product_id = str(product_id)

        if qty <= 0:
            self.remove(product_id)
        else:
            self.items[product_id] = qty

        self.save()

    # ------------------------
    # TOTAL PRICE
    # ------------------------
    def total(self):
        total = 0
        p = Product()

        for product_id, qty in self.items.items():
            product = p.get_product_by_id(product_id)
            if product:
                total += product.price * qty

        return total

    # ------------------------
    # DB FUNCTIONS
    # ------------------------
    def get_cart_from_db(self, user_id):
        cur = con.cursor()
        cur.execute("SELECT product_id, quantity FROM cart WHERE user_id = %s", (user_id,))
        rows = cur.fetchall()
        cur.close()

        cart = {}
        for row in rows:
            cart[str(row[0])] = row[1]

        return cart

    def save_cart_to_db(self, user_id):
        cur = con.cursor()

        # Clear old cart
        cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))

        # Insert new cart
        for product_id, quantity in self.items.items():
            cur.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                (user_id, product_id, quantity)
            )

        con.commit()
        cur.close()