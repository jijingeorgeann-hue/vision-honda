from pathlib import Path
from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "vision-honda-change-this-secret"

DB = "data/vision_honda.db"

def connect():
    os.makedirs("data", exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )""")
        con.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            model TEXT,
            followup TEXT,
            notes TEXT
        )""")
        con.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            variant TEXT,
            price REAL DEFAULT 0
        )""")
        if not con.execute("SELECT id FROM users").fetchone():
            con.execute(
                "INSERT INTO users(username,password,role) VALUES(?,?,?)",
                ("admin", "ChangeMe123!", "admin")
            )

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        with connect() as con:
            user = con.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            ).fetchone()
        if user:
            session["user"] = user["username"]
            session["role"] = user["role"]
            return redirect("/dashboard")
        flash("Invalid username or password")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    with connect() as con:
        count = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        customers = con.execute(
            "SELECT * FROM customers ORDER BY id DESC LIMIT 10"
        ).fetchall()
    return render_template(
        "dashboard.html",
        count=count,
        customers=customers,
        username=session["user"],
        role=session["role"]
    )

@app.route("/customers", methods=["GET", "POST"])
def customers():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Customer name is required")
            return redirect("/customers")
        with connect() as con:
            con.execute(
                """INSERT INTO customers(name,phone,model,followup,notes)
                VALUES(?,?,?,?,?)""",
                (
                    name,
                    request.form.get("phone", ""),
                    request.form.get("model", ""),
                    request.form.get("followup", ""),
                    request.form.get("notes", "")
                )
            )
        flash("Customer saved successfully")
        return redirect("/dashboard")
    return render_template("customers.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/media", methods=["GET", "POST"])
def media():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST" and session.get("role") != "admin":
        flash("Only Admin can upload files")
        return redirect("/media")

    categories = {
        "photos": {"label": "Photos", "extensions": {"jpg", "jpeg", "png", "webp"}},
        "videos": {"label": "Videos", "extensions": {"mp4", "mov"}},
        "brochures": {"label": "Brochures", "extensions": {"pdf"}},
        "price_lists": {"label": "Price Lists", "extensions": {"pdf"}}
    }

    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS media_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    if request.method == "POST":
        category = request.form.get("category", "")
        title = request.form.get("title", "").strip()
        uploaded = request.files.get("file")

        if category not in categories or not uploaded or not uploaded.filename:
            flash("Select a category and file")
            return redirect("/media")

        original = secure_filename(uploaded.filename)
        ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""

        if ext not in categories[category]["extensions"]:
            flash("File type not allowed")
            return redirect("/media")

        folder = Path("static/media") / category
        folder.mkdir(parents=True, exist_ok=True)
        filename = uuid.uuid4().hex + "." + ext
        filepath = folder / filename
        uploaded.save(str(filepath))

        with connect() as con:
            con.execute(
                "INSERT INTO media_files(title,category,filename,filepath) VALUES(?,?,?,?)",
                (title or original, category, original, str(filepath))
            )

        flash("File uploaded successfully")
        return redirect("/media")

    with connect() as con:
        files = con.execute(
            "SELECT * FROM media_files ORDER BY id DESC"
        ).fetchall()

    return render_template("media.html", files=files, categories=categories)

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
