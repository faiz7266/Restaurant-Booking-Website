
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import UserModel, ProductModel, CartModel, CATEGORIES
import os

app = Flask(__name__)
app.secret_key = "change-this-in-production"

# Models bound to JSON files
users = UserModel("data/users.json")
products = ProductModel("data/products.json")
cart = CartModel("data/purchases.json")

# ---------------------- Helpers ----------------------
def require_login():
    if "user" not in session:
        return False
    return True

# ---------------------- Routes ----------------------

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# -------- Authentication --------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        username = request.form.get("username","").strip()
        if not email or not password or not username:
            flash("All fields are required.", "danger")
            return redirect(url_for("signup"))
        if users.get_user(email):
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("signup"))
        users.add_user(email=email, password=password, username=username)
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        user = users.validate_login(email, password)
        if user:
            session["user"] = user["email"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# -------- User Dashboard (Profile) --------
@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))
    current = users.get_user(session["user"])
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    all_products = products.search_products(query=query, category=category)
    return render_template("dashboard.html", products=all_products, user=current, categories=CATEGORIES, q=query, selected_category=category)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not require_login():
        return redirect(url_for("login"))
    user = users.get_user(session["user"])
    if request.method == "POST":
        username = request.form.get("username","").strip()
        bio = request.form.get("bio","").strip()
        avatar = request.form.get("avatar","").strip()  # path/url placeholder
        users.update_user(user["email"], {"username": username or user["username"], "bio": bio, "avatar": avatar or user.get("avatar","")})
        flash("Profile updated.", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html", user=user)

# -------- Product CRUD --------
@app.route("/add", methods=["GET", "POST"])
def add_product():
    if not require_login():
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form.get("title","").strip()
        category = request.form.get("category","").strip()
        description = request.form.get("description","").strip()
        price = request.form.get("price","").strip()
        image = "static/placeholder.png"  # placeholder; extend to uploads if needed
        if not title or not category or not description or not price:
            flash("All fields are required.", "danger")
            return redirect(url_for("add_product"))
        products.add_product(owner=session["user"], title=title, category=category, description=description, price=price, image=image)
        flash("Product listed!", "success")
        return redirect(url_for("my_listings"))
    return render_template("add_product.html", categories=CATEGORIES)

@app.route("/my_listings")
def my_listings():
    if not require_login():
        return redirect(url_for("login"))
    my_products = products.get_user_products(session["user"])
    return render_template("my_listings.html", products=my_products)

@app.route("/product/<int:pid>")
def product_detail(pid):
    prod = products.get_product(pid)
    if not prod:
        flash("Product not found.", "danger")
        return redirect(url_for("dashboard"))
    owner = users.get_user(prod["owner"])
    return render_template("product_detail.html", product=prod, owner=owner)

@app.route("/product/<int:pid>/edit", methods=["GET","POST"])
def edit_product(pid):
    if not require_login():
        return redirect(url_for("login"))
    prod = products.get_product(pid)
    if not prod or prod["owner"] != session["user"]:
        flash("Unauthorized or product not found.", "danger")
        return redirect(url_for("my_listings"))
    if request.method == "POST":
        data = {
            "title": request.form.get("title","").strip(),
            "category": request.form.get("category","").strip(),
            "description": request.form.get("description","").strip(),
            "price": request.form.get("price","").strip(),
        }
        products.update_product(pid, data)
        flash("Product updated.", "success")
        return redirect(url_for("my_listings"))
    return render_template("edit_product.html", product=prod, categories=CATEGORIES)

@app.route("/product/<int:pid>/delete")
def delete_product(pid):
    if not require_login():
        return redirect(url_for("login"))
    products.delete_product(pid, session["user"])
    flash("Product deleted.", "info")
    return redirect(url_for("my_listings"))

# -------- Cart & Purchases --------
@app.route("/cart")
def cart_view():
    if not require_login():
        return redirect(url_for("login"))
    items = cart.get_cart(session["user"])
    total = sum(float(i["product"]["price"]) for i in items) if items else 0.0
    return render_template("cart.html", items=items, total=total)

@app.route("/cart/add/<int:pid>")
def add_to_cart(pid):
    if not require_login():
        return redirect(url_for("login"))
    prod = products.get_product(pid)
    if not prod:
        flash("Product not found.", "danger")
        return redirect(url_for("dashboard"))
    cart.add_to_cart(session["user"], prod)
    flash("Added to cart.", "success")
    return redirect(url_for("cart_view"))

@app.route("/cart/remove/<int:index>")
def remove_from_cart(index):
    if not require_login():
        return redirect(url_for("login"))
    cart.remove_from_cart(session["user"], index)
    flash("Removed from cart.", "info")
    return redirect(url_for("cart_view"))

@app.route("/purchase")
def purchase():
    if not require_login():
        return redirect(url_for("login"))
    cart.purchase_items(session["user"])
    flash("Purchase completed!", "success")
    return redirect(url_for("purchases"))

@app.route("/purchases")
def purchases():
    if not require_login():
        return redirect(url_for("login"))
    history = cart.get_purchases(session["user"])
    return render_template("purchases.html", items=history)

# ------------- Run -------------
if __name__ == "__main__":
    if not os.path.exists("data"): os.makedirs("data")
    app.run(debug=True)
