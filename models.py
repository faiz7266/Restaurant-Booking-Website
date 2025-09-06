
import json, os

CATEGORIES = ["Clothing", "Electronics", "Books", "Home", "Sports", "Other"]

class BaseModel:
    def __init__(self, filepath):
        self.filepath = filepath
        # Ensure file exists with sensible default structure
        if not os.path.exists(filepath):
            # Detect list vs dict default by filename
            default = [] if filepath.endswith(('.json')) else {}
            with open(filepath, "w") as f:
                json.dump(default, f)

    def load(self):
        with open(self.filepath, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

class UserModel(BaseModel):
    def get_user(self, email):
        users = self.load()
        return next((u for u in users if u["email"] == email), None)

    def add_user(self, email, password, username):
        users = self.load()
        # basic profile fields
        users.append({
            "email": email,
            "password": password,  # NOTE: plain text for prototype only
            "username": username,
            "bio": "",
            "avatar": "static/avatar_placeholder.png"
        })
        self.save(users)

    def validate_login(self, email, password):
        u = self.get_user(email)
        return u if u and u["password"] == password else None

    def update_user(self, email, updates: dict):
        users = self.load()
        for u in users:
            if u["email"] == email:
                u.update(updates)
                break
        self.save(users)

class ProductModel(BaseModel):
    def _next_id(self, products):
        return (max((p["id"] for p in products), default=0) + 1)

    def add_product(self, owner, title, category, description, price, image):
        products = self.load()
        pid = self._next_id(products)
        products.append({
            "id": pid,
            "owner": owner,
            "title": title,
            "category": category,
            "description": description,
            "price": str(price),
            "image": image
        })
        self.save(products)

    def get_product(self, pid):
        return next((p for p in self.load() if p["id"] == pid), None)

    def get_user_products(self, owner):
        return [p for p in self.load() if p["owner"] == owner]

    def update_product(self, pid, data):
        products = self.load()
        for p in products:
            if p["id"] == pid:
                for k,v in data.items():
                    if v != "":
                        p[k] = v
                break
        self.save(products)

    def delete_product(self, pid, owner):
        products = self.load()
        products = [p for p in products if not (p["id"] == pid and p["owner"] == owner)]
        self.save(products)

    def search_products(self, query="", category=""):
        prods = self.load()
        if query:
            q = query.lower()
            prods = [p for p in prods if q in p["title"].lower()]
        if category:
            prods = [p for p in prods if p["category"].lower() == category.lower()]
        return prods

class CartModel(BaseModel):
    def add_to_cart(self, user, product):
        data = self.load()
        data.append({"user": user, "product": product, "status": "cart"})
        self.save(data)

    def get_cart(self, user):
        # include index so we can remove by index
        cart_items = [d for d in self.load() if d["user"] == user and d["status"] == "cart"]
        # annotate with index within user's cart view
        # for removal we will remove by nth item for that user
        return cart_items

    def remove_from_cart(self, user, index):
        data = self.load()
        # collect indices for this user's cart items
        user_indices = [i for i, d in enumerate(data) if d["user"] == user and d["status"] == "cart"]
        if 0 <= index < len(user_indices):
            del data[user_indices[index]]
            self.save(data)

    def purchase_items(self, user):
        data = self.load()
        for d in data:
            if d["user"] == user and d["status"] == "cart":
                d["status"] = "purchased"
        self.save(data)

    def get_purchases(self, user):
        return [d for d in self.load() if d["user"] == user and d["status"] == "purchased"]
