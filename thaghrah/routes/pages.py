import os

from flask import jsonify, redirect, render_template, request, session, url_for

from thaghrah.auth.decorators import login_required
from thaghrah.content import GUIDE_PAGES, GUIDE_TAB_PDF_REL
from thaghrah.core.config import STATIC_DIR
from thaghrah.core.constants import PROTOCOL_NAMES
from thaghrah.db import get_db, queries as db_queries


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

    @app.route("/guide")
    @login_required
    def guide():
        tabs = PROTOCOL_NAMES + ["Cheat Sheet"]
        selected = (request.args.get("tab") or tabs[0]).strip()
        if selected not in tabs:
            selected = tabs[0]
        page_content = GUIDE_PAGES.get(selected)
        pdf_available = False
        selected_pdf = None
        rel_pdf = GUIDE_TAB_PDF_REL.get(selected)
        if rel_pdf:
            abs_pdf = os.path.join(STATIC_DIR, rel_pdf)
            if os.path.isfile(abs_pdf):
                selected_pdf = rel_pdf
                pdf_available = True
        pdf_download_name = os.path.basename(selected_pdf) if selected_pdf else ""
        return render_template(
            "guide.html",
            tabs=tabs,
            selected_tab=selected,
            page_content=page_content,
            selected_pdf=selected_pdf,
            pdf_available=pdf_available,
            pdf_download_name=pdf_download_name,
        )
