from flask import Flask, redirect, render_template, request, session, url_for
from classes.product import Product
from classes.user import User
from classes.cart import Cart
from classes.order import Order


app = Flask(__name__)
app.secret_key = "Bord1" # Flask crasher når noget gemmes i en session, hvis 'secret_key' ikke haves

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("username")
        password = request.form.get("password")

        print(email, password) 
        # just to see it DELETE LATER!!!!

        user = User(email=email, password=password, firstname=None, lastname=None, address=None, zip=None, city=None, country=None, phone=None)
        if user.login(email, password):
            return redirect(url_for("products"))
        else:
            return render_template("login.html", error="Forkert email eller password")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        address = request.form.get("address")
        zip = request.form.get("zip")
        city = request.form.get("city")
        country = request.form.get("country")
        phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User(firstname=firstname, lastname=lastname, address=address, zip=zip, city=city, country=country, phone=phone, email=email, password=password)

        if user.register(firstname, lastname, address, zip, city, country, phone, email, password):
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="Brugeren findes allerede")
        
    return render_template("register.html")

@app.route("/account")
def account():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_obj = User(email=None, password=None, firstname=None, lastname=None,
                    address=None, zip=None, city=None, country=None, phone=None)

    data = user_obj.get_user_info()

    # 🔥 Convert tuple → dictionary
    user_info = {
        "id": data[0],
        "email": data[1],
        "password": data[2],
        "firstname": data[3],
        "lastname": data[4],
        "address": data[5],
        "zip": data[6],
        "city": data[7],
        "country": data[8],
        "phone": data[9]
    }

    return render_template("account.html", user=user_info)

@app.route("/update", methods=["GET", "POST"])
def update():
    user = User(email=None, password=None, firstname=None, lastname=None, address=None, zip=None, city=None, country=None, phone=None) # Kalder først objektet for at kunne bruge 'get_user_info()' metoden, som henter nuværende oplysninger for den loggede bruger baseret på deres ID, som er gemt i sessionen
    user_info = user.get_user_info() # Henter nuværende oplysninger for den loggede bruger baseret på deres ID, som er gemt i sessionen

    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        address = request.form.get("address")
        zip = request.form.get("zip")
        city = request.form.get("city")
        country = request.form.get("country")
        phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")

        user.update(firstname, lastname, address, zip, city, country, phone, email, password)
        return redirect(url_for("home"))

    return render_template("update.html", user_info=user_info)

@app.route("/logout") # Ligger som knap under 'products.html'
def logout():
    session.clear() # Rydder sessionen, så brugeren bliver logget ud
    return redirect(url_for("home"))

@app.route("/products")
def products():
    # Create a Product instance to access the methods
    p = Product()
    all_products = p.get_products()       # Fetch all products
    #id_product = p.get_product_by_id(3)  # Example fetch by id
    #print("Product found by id:", id_product.name, id_product.price, "$", id_product.stock, "In stock")
    print("All products:", all_products)
    return render_template("products.html", products=all_products)






def get_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]








@app.route("/cart")
def view_cart():
    cart = Cart()
    p = Product()

    products_in_cart = []

    for product_id, quantity in cart.items.items():
        product = p.get_product_by_id(product_id)

        if product:
            products_in_cart.append({
                "product": product,
                "quantity": quantity,
                "subtotal": product.price * quantity
            })

    return render_template(
        "cart.html",
        cart_items=products_in_cart,
        total=cart.total()
    )

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_id = request.form.get("product_id")

    cart = Cart()
    cart.add(product_id)

    return redirect(url_for("products"))

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    product_id = request.form.get("product_id")

    cart = Cart()
    cart.remove(product_id)

    return redirect(url_for("view_cart"))

@app.route("/increase_quantity", methods=["POST"])
def increase_quantity():
    product_id = request.form.get("product_id")

    cart = Cart()
    current_qty = cart.items.get(str(product_id), 0)

    cart.update(product_id, current_qty + 1)

    return redirect(url_for("view_cart"))

@app.route("/decrease_quantity", methods=["POST"])
def decrease_quantity():
    product_id = request.form.get("product_id")

    cart = Cart()
    current_qty = cart.items.get(str(product_id), 0)

    cart.update(product_id, current_qty - 1)

    return redirect(url_for("view_cart"))


@app.route("/place_order", methods=["POST"])
def place_order():
    order = Order()
    success, result = order.place_order()

    if not success:
        return result

    return redirect(url_for("account"))

from classes.order import Order

@app.route("/orders")
def orders():
    if "user_id" not in session:
        return redirect(url_for("login"))

    order = Order()
    user_orders = order.get_orders_by_user(session["user_id"])

    return render_template("orders.html", orders=user_orders)


@app.route("/cancel_order", methods=["POST"])
def cancel_order():
    order_id = request.form.get("order_id")

    order = Order()
    success, message = order.cancel_order(order_id)

    if not success:
        return message

    return redirect(url_for("orders"))


app.run(debug=True)
