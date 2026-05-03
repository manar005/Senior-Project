from flask import redirect, render_template, session, url_for, jsonify

import db_queries

from thaghrah.database import get_db
from thaghrah.decorators import login_required


def register_routes(app):
    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("home"))
        return render_template("start.html")

    @app.route("/home")
    @login_required
    def home():
        conn = get_db()
        user_badges = db_queries.get_user_badges(conn, session["user_id"])
        total_badges = db_queries.get_total_badges_count(conn)
        total_points = db_queries.get_user_total_points(conn, session["user_id"])
        conn.close()
        return render_template(
            "home.html",
            user_badges=user_badges,
            total_badges=total_badges,
            total_points=total_points,
        )

    @app.route("/api/me")
    @login_required
    def api_me():
        conn = get_db()
        total_points = db_queries.get_user_total_points(conn, session["user_id"])
        badges = db_queries.get_user_badges(conn, session["user_id"])
        conn.close()
        return jsonify({"points": total_points, "badges": len(badges)})
