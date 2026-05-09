import sqlite3

from flask import redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from thaghrah.db import get_db, queries as db_queries
from thaghrah.domain.challenge_utils import validate_password


def register_routes(app):
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if not name or not email or not password or not confirm_password:
                return render_template("register.html", error="All fields are required")

            if password != confirm_password:
                return render_template("register.html", error="Passwords do not match")

            conn = get_db()
            existing = db_queries.get_user_by_email(conn, email)
            if existing:
                conn.close()
                return render_template(
                    "register.html",
                    error="This email is already registered. Please sign in or use a different email.",
                )

            valid, msg = validate_password(password)
            if not valid:
                conn.close()
                return render_template("register.html", error=msg)

            try:
                password_hash = generate_password_hash(password)
                user_id = db_queries.create_user(conn, name, email, password_hash)
                conn.close()

                session["user_id"] = user_id
                session["email"] = email
                session["name"] = name
                return redirect(url_for("home"))
            except sqlite3.IntegrityError:
                conn.close()
                return render_template(
                    "register.html",
                    error="This email is already registered. Please sign in or use a different email.",
                )

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password")

            if not email or not password:
                return render_template("login.html", error="Email and password are required")

            conn = get_db()
            user = db_queries.get_user_by_email(conn, email)
            conn.close()

            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["email"] = user["email"]
                if "name" in user.keys() and user["name"]:
                    session["name"] = user["name"]
                return redirect(url_for("home"))
            else:
                return render_template("login.html", error="Invalid email or password")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))
