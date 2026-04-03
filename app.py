from flask import Flask, redirect, render_template, request, url_for
from classes.product import Product
from classes.user import User


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
            return render_template("products.html")
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

@app.route("/products")
def products():
    # Create a Product instance to access the methods
    p = Product()
    all_products = p.get_products()       # Fetch all products
    id_product = p.get_product_by_id(3)  # Example fetch by id
    print("Product found by id:", id_product.name, id_product.price, "$", id_product.stock, "In stock")
    print("All products:", all_products)
    return render_template("products.html", products=all_products)

app.run(debug=True)
