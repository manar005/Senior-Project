import time

from flask import current_app, jsonify, redirect, render_template, request, session, url_for

from challenges import (
    NETWORK_CHALLENGE_COUNT,
    challenge_dict_for_db_id,
    is_valid_network_challenge_id,
)

from thaghrah.ai.challenge_payload import parse_bool
from thaghrah.auth.decorators import login_required
from thaghrah.core.constants import PROTOCOL_NAMES
from thaghrah.db import get_db, queries as db_queries
from thaghrah.domain.challenge_utils import (
    _flag_fingerprint,
    check_and_award_badges,
    get_protocol_details,
    get_unlocked_challenges,
    network_flag_match,
    protocol_guide_pdf_rel_path,
)


def register_routes(app):
    @app.route("/challenges/network")
    @login_required
    def network_challenges():
        conn = get_db()
        categories = db_queries.get_all_categories(conn)
        all_challenges = db_queries.get_all_challenges(conn)
        completed = db_queries.get_user_progress(conn, session["user_id"])
        completed_ids = [row[0] for row in completed]
        unlocked = get_unlocked_challenges(all_challenges, completed_ids)
        categories_with_challenges = []
        for protocol_name in PROTOCOL_NAMES:
            primary = next((c for c in categories if c["title"] == protocol_name), None)
            if not primary:
                continue
            if protocol_name == "TCP":
                tcp_cat_ids = [c["id"] for c in categories if c["title"] == "TCP" or c["title"].startswith("TCP ")]
                challenges_in_cat = db_queries.get_challenges_by_category_ids(conn, tcp_cat_ids)
            else:
                challenges_in_cat = db_queries.get_challenges_by_category(conn, primary["id"])
            categories_with_challenges.append({"category": primary, "challenges": challenges_in_cat})
        user_badges = db_queries.get_user_badges(conn, session["user_id"])
        total_badges = db_queries.get_total_badges_count(conn)
        total_points = db_queries.get_user_total_points(conn, session["user_id"])
        conn.close()
        return render_template(
            "dashboard.html",
            categories_with_challenges=categories_with_challenges,
            all_challenges=all_challenges,
            completed_ids=completed_ids,
            unlocked=unlocked,
            category="Network Security",
            user_badges=user_badges,
            total_badges=total_badges,
            total_points=total_points,
        )

    @app.route("/challenges/network/category/<int:category_id>")
    @login_required
    def category_challenges(category_id):
        conn = get_db()
        cat = db_queries.get_category_by_id(conn, category_id)
        if not cat:
            conn.close()
            return redirect(url_for("network_challenges"))
        all_challenges = db_queries.get_all_challenges(conn)
        completed = db_queries.get_user_progress(conn, session["user_id"])
        completed_ids = [row[0] for row in completed]
        unlocked = get_unlocked_challenges(all_challenges, completed_ids)
        if cat["title"] == "TCP":
            categories = db_queries.get_all_categories(conn)
            tcp_cat_ids = [c["id"] for c in categories if c["title"] == "TCP" or c["title"].startswith("TCP ")]
            challenges = db_queries.get_challenges_by_category_ids(conn, tcp_cat_ids)
        else:
            challenges = db_queries.get_challenges_by_category(conn, category_id)
        user_badges = db_queries.get_user_badges(conn, session["user_id"])
        total_badges = db_queries.get_total_badges_count(conn)
        total_points = db_queries.get_user_total_points(conn, session["user_id"])
        completed_in_category = sum(1 for c in challenges if c["id"] in completed_ids)
        category_completed = (completed_in_category == len(challenges)) if challenges else False
        categories_ordered = db_queries.get_all_categories(conn)
        next_category = None
        previous_category = None
        for i, c in enumerate(categories_ordered):
            if c["id"] == cat["id"]:
                if i + 1 < len(categories_ordered):
                    next_category = categories_ordered[i + 1]
                if i > 0:
                    previous_category = categories_ordered[i - 1]
                break
        conn.close()
        return render_template(
            "category_challenges.html",
            category=cat,
            protocol_details=get_protocol_details(cat["title"]),
            challenges=challenges,
            completed_ids=completed_ids,
            completed_in_category=completed_in_category,
            unlocked=unlocked,
            all_challenges=all_challenges,
            user_badges=user_badges,
            total_badges=total_badges,
            total_points=total_points,
            category_completed=category_completed,
            next_category=next_category,
            previous_category=previous_category,
            protocol_guide_pdf=protocol_guide_pdf_rel_path(cat["title"]),
        )

    @app.route("/challenge/<int:challenge_id>")
    @login_required
    def challenge(challenge_id):
        if not is_valid_network_challenge_id(challenge_id):
            return redirect(url_for("network_challenges"))
        conn = get_db()
        challenge_row = db_queries.get_challenge_by_id(conn, challenge_id)
        if not challenge_row:
            conn.close()
            return redirect(url_for("network_challenges"))
        challenges = db_queries.get_all_challenges(conn)
        completed = db_queries.get_user_progress(conn, session["user_id"])
        completed_ids = [row[0] for row in completed]
        unlocked = get_unlocked_challenges(challenges, completed_ids)
        if challenge_id not in unlocked:
            conn.close()
            return redirect(url_for("network_challenges"))
        conn.close()
        return render_template(
            "challenge.html",
            challenge=challenge_row,
            is_completed=challenge_id in completed_ids,
            category_url=url_for("category_challenges", category_id=challenge_row["category_id"]),
        )

    @app.route("/submit_flag", methods=["POST"])
    @login_required
    def submit_flag():
        started = time.perf_counter()
        data = request.get_json(silent=True) or {}
        challenge_id = data.get("challenge_id")
        flag = data.get("flag")
        used_hint = parse_bool(data.get("used_hint"), False)

        if challenge_id is None or flag is None:
            current_app.logger.warning(
                "SUBMIT_FLAG missing_fields challenge_id=%r user_id=%s",
                challenge_id,
                session.get("user_id"),
            )
            return jsonify({"success": False, "message": "Missing challenge ID or flag"})
        flag = str(flag).strip()
        if not flag:
            current_app.logger.warning(
                "SUBMIT_FLAG empty_flag challenge_id=%r user_id=%s",
                challenge_id,
                session.get("user_id"),
            )
            return jsonify({"success": False, "message": "Please enter a flag"})
        try:
            challenge_id = int(challenge_id)
            if not is_valid_network_challenge_id(challenge_id):
                current_app.logger.warning(
                    "SUBMIT_FLAG invalid_challenge_id challenge_id=%r user_id=%s",
                    challenge_id,
                    session.get("user_id"),
                )
                return jsonify({"success": False, "message": "Invalid challenge ID"})
        except (ValueError, TypeError):
            current_app.logger.warning(
                "SUBMIT_FLAG invalid_challenge_id challenge_id=%r user_id=%s",
                challenge_id,
                session.get("user_id"),
            )
            return jsonify({"success": False, "message": "Invalid challenge ID"})

        conn = get_db()
        challenge_row = db_queries.get_challenge_by_id(conn, challenge_id)

        if not challenge_row:
            conn.close()
            current_app.logger.warning(
                "SUBMIT_FLAG challenge_not_found challenge_id=%s user_id=%s",
                challenge_id,
                session.get("user_id"),
            )
            return jsonify({"success": False, "message": "Challenge not found"})

        stored_flag = challenge_row["flag"]
        if stored_flag is None:
            stored_flag = ""
        # Prefer matching against the Python challenge definition so a stale or
        # wrong-copy thaghrah.db cannot reject the correct flag (DB is still used
        # for title, points, progress, etc.).
        canonical_flag = None
        try:
            canonical_flag = challenge_dict_for_db_id(challenge_id).get("flag")
        except (ValueError, TypeError, KeyError):
            pass
        flag_ok = network_flag_match(stored_flag, flag) or (
            canonical_flag is not None and network_flag_match(canonical_flag, flag)
        )
        if flag_ok:
            existing = db_queries.check_challenge_completed(conn, session["user_id"], challenge_id)
            new_badges = []
            badge_message = ""
            points_earned = 0
            base_points = 100
            if "points" in challenge_row.keys():
                try:
                    base_points = int(challenge_row["points"])
                except (TypeError, ValueError):
                    pass
            if used_hint:
                points_earned = max(0, base_points // 2)
            else:
                points_earned = base_points
            if not existing:
                db_queries.complete_challenge(
                    conn,
                    session["user_id"],
                    challenge_id,
                    used_hint=used_hint,
                    points_earned=points_earned,
                )
                new_badges = check_and_award_badges(session["user_id"])
                if new_badges:
                    badge_names = [badge["name"] for badge in new_badges]
                    badge_message = f' 🏆 Badge earned: {", ".join(badge_names)}!'
            completed_rows = db_queries.get_user_progress(conn, session["user_id"])
            completed_count = len({row[0] for row in completed_rows})
            total_network_challenges = NETWORK_CHALLENGE_COUNT
            all_challenges_completed = completed_count >= total_network_challenges

            conn.close()
            current_app.logger.info(
                "SUBMIT_FLAG success challenge_id=%s user_id=%s used_hint=%s points=%s completed=%s/%s all_completed=%s elapsed_ms=%.2f submitted=%s",
                challenge_id,
                session.get("user_id"),
                used_hint,
                points_earned,
                completed_count,
                total_network_challenges,
                all_challenges_completed,
                (time.perf_counter() - started) * 1000.0,
                _flag_fingerprint(flag),
            )
            message = f"Correct! Challenge completed! +{points_earned} points." + badge_message
            return jsonify(
                {
                    "success": True,
                    "message": message,
                    "new_badges": new_badges,
                    "points_earned": points_earned,
                    "completed_count": completed_count,
                    "total_challenges": total_network_challenges,
                    "all_challenges_completed": all_challenges_completed,
                }
            )
        conn.close()
        current_app.logger.info(
            "SUBMIT_FLAG incorrect challenge_id=%s user_id=%s elapsed_ms=%.2f submitted=%s",
            challenge_id,
            session.get("user_id"),
            (time.perf_counter() - started) * 1000.0,
            _flag_fingerprint(flag),
        )
        return jsonify({"success": False, "message": "Incorrect flag. Try again!"})
