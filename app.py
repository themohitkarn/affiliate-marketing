from flask import Flask, render_template, request, redirect, session, url_for
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import init_db


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")   # change later in production

@app.before_first_request
def setup_database():
    init_db()



# ======================
# ADMIN CREDENTIALS
# ======================
ADMIN_USERNAME = "admin"

# password: admin123
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")


# ======================
# DATABASE HELPER
# ======================
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ======================
# PUBLIC ROUTES
# ======================

@app.route("/")
def index():
    category = request.args.get("category")
    db = get_db()

    if category:
        products = db.execute(
            "SELECT * FROM products WHERE category=?",
            (category,)
        ).fetchall()
    else:
        products = db.execute(
            "SELECT * FROM products"
        ).fetchall()

    categories = db.execute(
        "SELECT DISTINCT category FROM products"
    ).fetchall()

    return render_template(
        "index.html",
        products=products,
        categories=categories
    )


@app.route("/product/<int:id>")
def product_detail(id):
    db = get_db()
    product = db.execute(
        "SELECT * FROM products WHERE id=?",
        (id,)
    ).fetchone()

    if not product:
        return redirect("/")

    return render_template(
        "product_detail.html",
        product=product
    )


# ======================
# CLICK TRACKING + REDIRECT
# ======================

@app.route("/go/<int:id>")
def go(id):
    db = get_db()

    db.execute(
        "UPDATE products SET clicks = clicks + 1 WHERE id=?",
        (id,)
    )
    db.commit()

    product = db.execute(
        "SELECT affiliate_link FROM products WHERE id=?",
        (id,)
    ).fetchone()

    if product:
        return redirect(product["affiliate_link"])

    return redirect("/")


# ======================
# ADMIN AUTH
# ======================

@app.route("/admin-mohit-ankit-73200", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if (
            username == ADMIN_USERNAME
            and check_password_hash(ADMIN_PASSWORD_HASH, password)
        ):
            session["admin"] = True
            return redirect("/dashboard")

    return render_template("admin_login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")


# ======================
# ADMIN DASHBOARD
# ======================

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    db = get_db()
    products = db.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    return render_template(
        "admin_dashboard.html",
        products=products
    )


# ======================
# ADD PRODUCT
# ======================

@app.route("/add", methods=["GET", "POST"])
def add_product():
    if not session.get("admin"):
        return redirect("/admin")

    if request.method == "POST":
        title = request.form["title"]
        image = request.form["image"]
        category = request.form["category"]
        description = request.form["description"]
        affiliate_link = request.form["affiliate_link"]

        db = get_db()
        db.execute(
            """
            INSERT INTO products
            (title, description, image, category, affiliate_link, clicks)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (title, description, image, category, affiliate_link)
        )
        db.commit()

        return redirect("/dashboard")

    return render_template("add_product.html")


# ======================
# EDIT PRODUCT
# ======================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    if not session.get("admin"):
        return redirect("/admin")

    db = get_db()

    if request.method == "POST":
        db.execute(
            """
            UPDATE products
            SET title=?, description=?, image=?, category=?, affiliate_link=?
            WHERE id=?
            """,
            (
                request.form["title"],
                request.form["description"],
                request.form["image"],
                request.form["category"],
                request.form["affiliate_link"],
                id
            )
        )
        db.commit()
        return redirect("/dashboard")

    product = db.execute(
        "SELECT * FROM products WHERE id=?",
        (id,)
    ).fetchone()

    return render_template(
        "edit_product.html",
        product=product
    )


# ======================
# DELETE PRODUCT
# ======================

@app.route("/delete/<int:id>")
def delete_product(id):
    if not session.get("admin"):
        return redirect("/admin")

    db = get_db()
    db.execute(
        "DELETE FROM products WHERE id=?",
        (id,)
    )
    db.commit()

    return redirect("/dashboard")


# ======================
# RUN APP
# ======================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
