import os
import time

from flask import abort, current_app, jsonify, render_template, request, send_file, session, url_for

import db_queries
from ai_challenge_utils import extract_flag_inner_value, trim_only
from grok_challenge_client import call_grok_for_challenge
from pcap_from_ai_plan import build_packets_from_plan, make_ai_pcap_filename, write_pcap_with_tshark

from thaghrah.ai_helpers import (
    build_ai_hint,
    decode_with_encoding,
    encode_with_encoding,
    requested_encoding_from_prompt,
    requested_fragmentation_from_prompt,
)
from thaghrah.challenge_utils import _flag_fingerprint, _resolve_ai_pcap_path
from thaghrah.config import STATIC_DIR
from thaghrah.database import get_db
from thaghrah.decorators import login_required


def register_routes(app):
    @app.route("/challenges/ai")
    @login_required
    def ai_challenge_lab():
        return render_template("ai_challenge.html")

    @app.route("/challenges/ai/generate", methods=["POST"])
    @login_required
    def ai_challenge_generate():
        data = request.get_json(silent=True) or {}
        prompt = (data.get("prompt") or "").strip()
        if not prompt:
            return jsonify({"success": False, "message": "Please enter a prompt."}), 400

        ok, err_msg, payload = call_grok_for_challenge(prompt)
        if not ok or not payload:
            return jsonify({"success": False, "message": err_msg or "Generation failed."}), 400

        display_flag = payload.get("display_flag") or payload.get("flag")
        answer_flag = trim_only(payload.get("answer_flag"))
        display_inner = extract_flag_inner_value(display_flag or "")
        if not display_inner or not answer_flag:
            return jsonify({"success": False, "message": "Could not build a valid challenge. Try again."}), 400
        encoding = str(payload.get("encoding") or "none").strip().lower() or "none"
        requested_encoding = requested_encoding_from_prompt(prompt)
        requested_fragmentation = requested_fragmentation_from_prompt(prompt)
        frag_val = payload.get("fragmentation")
        if isinstance(frag_val, str):
            fragmentation = frag_val.strip().lower() in ("1", "true", "yes", "y")
        else:
            fragmentation = bool(frag_val)
        try:
            fragment_count = int(payload.get("fragment_count") or (4 if fragmentation else 1))
        except (TypeError, ValueError):
            fragment_count = 4 if fragmentation else 1
        if requested_fragmentation is not None:
            fragmentation = requested_fragmentation
        elif requested_encoding and not fragmentation:
            pass
        elif requested_encoding and fragmentation:
            fragmentation = False
        if not fragmentation:
            fragment_count = 1
        if encoding != "none":
            decoded_from_display = decode_with_encoding(display_inner, encoding)
            decoded_from_answer = decode_with_encoding(answer_flag, encoding)
            if decoded_from_display:
                answer_flag = decoded_from_display
            elif decoded_from_answer:
                display_flag = f'FLAG = "{answer_flag}"'
                display_inner = answer_flag
                answer_flag = decoded_from_answer
            if display_inner == answer_flag:
                return jsonify({"success": False, "message": "Generated challenge was malformed. Please try again."}), 400
        elif requested_encoding:
            encoding = requested_encoding
            encoded_value = encode_with_encoding(answer_flag, encoding)
            if encoded_value and encoded_value != answer_flag:
                display_flag = f'FLAG = "{encoded_value}"'
                display_inner = encoded_value

        if encoding == "none":
            display_inner = answer_flag
        else:
            encoded_value = encode_with_encoding(answer_flag, encoding)
            if encoded_value:
                display_inner = encoded_value
        display_flag = f'FLAG = "{display_inner}"'

        try:
            packets = build_packets_from_plan(
                payload["pcap_plan"],
                display_flag,
                answer_flag,
                fragmentation=fragmentation,
                fragment_count=fragment_count,
            )
        except Exception:
            return jsonify({"success": False, "message": "Could not build the capture file. Try again."}), 500

        hint = build_ai_hint(payload["protocol"], fragmentation, encoding)

        fname = make_ai_pcap_filename(session["user_id"])
        rel_pcap = f"pcaps/{fname}"
        abs_pcap = os.path.join(STATIC_DIR, rel_pcap)
        try:
            write_pcap_with_tshark(packets, abs_pcap)
        except Exception:
            return jsonify({"success": False, "message": "Could not save the capture file. Try again."}), 500

        conn = get_db()
        try:
            new_id = db_queries.insert_ai_challenge(
                conn,
                session["user_id"],
                payload["title"],
                payload["description"],
                hint,
                payload["outcome"],
                payload["points"],
                display_flag,
                answer_flag,
                payload["protocol"],
                payload["difficulty"],
                rel_pcap,
                prompt[:4000],
            )
        except Exception:
            conn.close()
            try:
                os.unlink(abs_pcap)
            except OSError:
                pass
            return jsonify({"success": False, "message": "Could not save the challenge. Try again."}), 500
        conn.close()

        return jsonify(
            {
                "success": True,
                "challenge": {
                    "id": new_id,
                    "title": payload["title"],
                    "description": payload["description"],
                    "outcome": payload["outcome"],
                    "points": payload["points"],
                    "protocol": payload["protocol"],
                    "difficulty": payload["difficulty"],
                    "encoding": encoding,
                    "fragmentation": fragmentation,
                    "download_url": url_for("ai_challenge_download", ai_id=new_id),
                },
            }
        )

    @app.route("/challenges/ai/hint", methods=["POST"])
    @login_required
    def ai_challenge_hint():
        data = request.get_json(silent=True) or {}
        try:
            ai_id = int(data.get("ai_challenge_id"))
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "Invalid challenge."}), 400

        conn = get_db()
        row = db_queries.get_ai_challenge_for_user(conn, ai_id, session["user_id"])
        if not row:
            conn.close()
            return jsonify({"success": False, "message": "Challenge not found."}), 404
        if row["completed"]:
            conn.close()
            return jsonify({"success": False, "message": "This challenge is already completed."}), 400

        db_queries.mark_ai_challenge_hint_used(conn, ai_id, session["user_id"])
        row = db_queries.get_ai_challenge_for_user(conn, ai_id, session["user_id"])
        conn.close()
        return jsonify({"success": True, "hint": row["hint"]})

    @app.route("/challenges/ai/submit-flag", methods=["POST"])
    @login_required
    def ai_challenge_submit_flag():
        started = time.perf_counter()
        data = request.get_json(silent=True) or {}
        try:
            ai_id = int(data.get("ai_challenge_id"))
        except (TypeError, ValueError):
            current_app.logger.warning(
                "AI_SUBMIT invalid_challenge_id challenge_id=%r user_id=%s",
                data.get("ai_challenge_id"),
                session.get("user_id"),
            )
            return jsonify({"success": False, "message": "Invalid challenge."}), 400

        flag = data.get("flag")
        if flag is None or not str(flag).strip():
            current_app.logger.warning(
                "AI_SUBMIT empty_flag challenge_id=%s user_id=%s",
                ai_id,
                session.get("user_id"),
            )
            return jsonify({"success": False, "message": "Please enter the flag value."}), 400

        conn = get_db()
        row = db_queries.get_ai_challenge_for_user(conn, ai_id, session["user_id"])
        if not row:
            conn.close()
            current_app.logger.warning(
                "AI_SUBMIT challenge_not_found challenge_id=%s user_id=%s",
                ai_id,
                session.get("user_id"),
            )
            return jsonify({"success": False, "message": "Challenge not found."}), 404
        if row["completed"]:
            conn.close()
            current_app.logger.info(
                "AI_SUBMIT already_completed challenge_id=%s user_id=%s",
                ai_id,
                session.get("user_id"),
            )
            return jsonify({"success": False, "message": "You already solved this challenge."})

        submitted = trim_only(flag)
        answer_flag = trim_only(row["answer_flag"]) if "answer_flag" in row.keys() else ""
        if not answer_flag:
            answer_flag = extract_flag_inner_value(row["flag"]) or trim_only(row["flag"])

        if submitted != answer_flag:
            conn.close()
            current_app.logger.info(
                "AI_SUBMIT incorrect challenge_id=%s user_id=%s elapsed_ms=%.2f submitted=%s answer=%s",
                ai_id,
                session.get("user_id"),
                (time.perf_counter() - started) * 1000.0,
                _flag_fingerprint(submitted),
                _flag_fingerprint(answer_flag),
            )
            return jsonify({"success": False, "message": "Incorrect flag. Try again!"})

        base_points = int(row["points"]) if row["points"] else 100
        used_hint = bool(row["hint_used"])
        awarded = max(0, base_points // 2) if used_hint else base_points

        if db_queries.complete_ai_challenge(conn, session["user_id"], ai_id, awarded):
            conn.close()
            current_app.logger.info(
                "AI_SUBMIT success challenge_id=%s user_id=%s used_hint=%s points=%s elapsed_ms=%.2f submitted=%s",
                ai_id,
                session.get("user_id"),
                used_hint,
                awarded,
                (time.perf_counter() - started) * 1000.0,
                _flag_fingerprint(submitted),
            )
            return jsonify(
                {
                    "success": True,
                    "message": f"Correct! +{awarded} points.",
                    "points_earned": awarded,
                    "used_hint": used_hint,
                }
            )
        row2 = db_queries.get_ai_challenge_for_user(conn, ai_id, session["user_id"])
        conn.close()
        if row2 and row2["completed"]:
            current_app.logger.info(
                "AI_SUBMIT already_recorded challenge_id=%s user_id=%s elapsed_ms=%.2f",
                ai_id,
                session.get("user_id"),
                (time.perf_counter() - started) * 1000.0,
            )
            return jsonify(
                {
                    "success": True,
                    "message": "Already solved — points were awarded earlier.",
                    "points_earned": row2["awarded_points"],
                    "used_hint": bool(row2["hint_used"]),
                }
            )
        current_app.logger.error(
            "AI_SUBMIT completion_write_failed challenge_id=%s user_id=%s elapsed_ms=%.2f",
            ai_id,
            session.get("user_id"),
            (time.perf_counter() - started) * 1000.0,
        )
        return jsonify({"success": False, "message": "Could not record completion. Try again."})

    @app.route("/challenges/ai/download/<int:ai_id>")
    @login_required
    def ai_challenge_download(ai_id):
        conn = get_db()
        row = db_queries.get_ai_challenge_for_user(conn, ai_id, session["user_id"])
        conn.close()
        if not row:
            abort(404)
        abs_path = _resolve_ai_pcap_path(row["pcap_path"])
        if not abs_path:
            abort(404)
        return send_file(abs_path, as_attachment=True, download_name=os.path.basename(abs_path))
