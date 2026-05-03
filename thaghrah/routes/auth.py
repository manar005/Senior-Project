import os
import secrets
import sqlite3
from datetime import datetime, timedelta

from flask import redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import db_queries

from thaghrah.challenge_utils import validate_password
from thaghrah.database import get_db
from thaghrah.mail import send_reset_link_email


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

        success = request.args.get("reset") == "1"
        return render_template("login.html", success=success)

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            if not email:
                return render_template("forgot_password.html", error="Please enter your email")
            conn = get_db()
            user = db_queries.get_user_by_email(conn, email)
            conn.close()
            if not user:
                return render_template("forgot_password.html", error="No account found with that email")
            token = secrets.token_urlsafe(32)
            expires_at = (datetime.utcnow() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
            conn = get_db()
            db_queries.create_reset_code(conn, email, token, expires_at)
            conn.close()
            reset_link = url_for("reset_password", token=token, _external=True)
            send_reset_link_email(email, reset_link)
            demo_link = reset_link if not os.environ.get("MAIL_SERVER") else None
            return render_template("forgot_password.html", success=True, email=email, demo_link=demo_link)
        return render_template("forgot_password.html")

    @app.route("/reset-password", methods=["GET", "POST"])
    def reset_password():
        token = request.args.get("token")
        if token:
            conn = get_db()
            row = db_queries.get_valid_reset_by_token(conn, token)
            conn.close()
            if row:
                session["reset_email"] = row["email"]
                session["reset_token"] = token
                return redirect(url_for("reset_password"))
            return render_template(
                "reset_password.html",
                error="This link is invalid or has expired. Please request a new one.",
            )
        reset_email = session.get("reset_email")
        reset_token = session.get("reset_token")
        if not reset_email or not reset_token:
            return redirect(url_for("forgot_password"))
        if request.method == "POST":
            new_password = request.form.get("new_password") or ""
            confirm_password = request.form.get("confirm_password") or ""
            if not new_password or not confirm_password:
                return render_template(
                    "reset_password.html",
                    reset_email=reset_email,
                    error="Both password fields are required",
                )
            if new_password != confirm_password:
                return render_template(
                    "reset_password.html",
                    reset_email=reset_email,
                    error="Passwords do not match",
                )
            valid, msg = validate_password(new_password)
            if not valid:
                return render_template("reset_password.html", reset_email=reset_email, error=msg)
            conn = get_db()
            row = db_queries.get_valid_reset_by_token(conn, reset_token)
            if not row or row["email"] != reset_email:
                conn.close()
                session.pop("reset_email", None)
                session.pop("reset_token", None)
                return render_template(
                    "reset_password.html",
                    error="This link has expired. Please request a new one from Forgot password.",
                )
            db_queries.invalidate_reset_code(conn, reset_email)
            password_hash = generate_password_hash(new_password)
            db_queries.update_user_password(conn, reset_email, password_hash)
            conn.close()
            session.pop("reset_email", None)
            session.pop("reset_token", None)
            return redirect(url_for("login") + "?reset=1")
        return render_template("reset_password.html", reset_email=reset_email)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))
