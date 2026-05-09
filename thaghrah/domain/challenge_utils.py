"""Challenge display, unlock logic, badges, and flag helpers."""
import hashlib
import os
from datetime import date

from thaghrah.ai.challenge_payload import extract_flag_inner_value, trim_only
from thaghrah.db import queries as db_queries

from thaghrah.core.config import PCAPS_DIR, STATIC_DIR
from thaghrah.content.protocol_details import PROTOCOL_DETAILS
from thaghrah.core.constants import PROTOCOL_NAMES
from thaghrah.db.database import get_db


def normalize_network_flag(s):
    """Normalize user or stored flag for comparison (case-insensitive, strip noise)."""
    if s is None:
        return ""
    if isinstance(s, bytes):
        s = s.decode("utf-8", errors="ignore")
    s = str(s).strip().replace("\r", "").replace("\n", "")
    for c in "\ufeff\u200b\u200c\u200d\u200e\u200f":
        s = s.replace(c, "")
    return s.upper()


def network_flag_match(stored_raw, submitted_raw) -> bool:
    """
    True if submitted flag matches stored challenge flag.
    Accepts plain tokens or FLAG = "value" style on either side.
    """
    submitted_str = str(submitted_raw or "").strip()
    if not submitted_str:
        return False
    inner_sub = extract_flag_inner_value(submitted_str)
    ns = normalize_network_flag(inner_sub if inner_sub is not None else submitted_str)
    if not ns:
        return False
    if isinstance(stored_raw, bytes):
        stored_raw = stored_raw.decode("utf-8", errors="ignore")
    stored_str = str(stored_raw or "")
    inner_st = extract_flag_inner_value(stored_str)
    candidates = {normalize_network_flag(stored_str)}
    if inner_st is not None:
        candidates.add(normalize_network_flag(inner_st))
    return ns in candidates


def _flag_fingerprint(value):
    value = trim_only(value)
    digest = hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:10]
    return f"len={len(value)} sha256={digest}"


def _resolve_ai_pcap_path(rel_path):
    """Ensure AI PCAP download stays under static/pcaps/. Returns absolute path or None."""
    if not rel_path or not isinstance(rel_path, str):
        return None
    if ".." in rel_path or rel_path.startswith(("/", "\\")):
        return None
    rel_path = rel_path.replace("\\", "/").lstrip("/")
    if not rel_path.startswith("pcaps/"):
        return None
    base = os.path.abspath(PCAPS_DIR)
    full = os.path.abspath(os.path.join(STATIC_DIR, rel_path))
    if not full.startswith(base + os.sep) and full != base:
        return None
    if not os.path.isfile(full):
        return None
    return full


def validate_password(password):
    """Validate password: at least 8 chars, one uppercase letter, one special character."""
    import re

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one capital letter."
    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain at least one special character."
    return True, None


def get_protocol_details(protocol_name):
    return PROTOCOL_DETAILS.get(
        protocol_name,
        {
            "overview": "Explore this protocol through hands-on packet analysis challenges.",
            "common_ports": "Varies by implementation",
            "focus": "Traffic structure, message flow, and observable indicators.",
            "why_it_matters": "Learning this protocol improves your network analysis and incident response skills.",
        },
    )


def _protocol_key_for_pdf(category_title):
    """Map category row title to a PROTOCOL_NAMES label (PDFs use e.g. 'HTTP Protocol Guide.pdf')."""
    t = (category_title or "").strip()
    if not t:
        return None
    if t == "TCP" or t.startswith("TCP "):
        return "TCP"
    for name in PROTOCOL_NAMES:
        if t == name:
            return name
    return None


def protocol_guide_pdf_rel_path(category_title):
    """Relative path under static/ for the protocol PDF if the file exists, else None."""
    key = _protocol_key_for_pdf(category_title)
    if not key:
        return None
    filename = f"{key} Protocol Guide.pdf"
    full = os.path.join(STATIC_DIR, "pdfs", filename)
    if os.path.isfile(full):
        return f"pdfs/{filename}"
    return None


def check_and_award_badges(user_id):
    """Check if user qualifies for any badges and award them."""
    conn = get_db()

    completed = db_queries.get_user_progress(conn, user_id)
    completed_ids = [row[0] for row in completed]
    total_completed = len(completed_ids)

    badges = db_queries.get_all_badges(conn)
    user_badge_ids = db_queries.get_user_badge_ids(conn, user_id)
    new_badges = []

    for badge in badges:
        if badge["id"] in user_badge_ids:
            continue

        requirement_type = badge["requirement_type"]
        requirement_value = badge["requirement_value"]
        if requirement_type == "challenges_completed":
            if total_completed >= requirement_value:
                if db_queries.award_badge(conn, user_id, badge["id"]):
                    new_badges.append(dict(badge))

        elif requirement_type == "daily_challenges":
            today = date.today().isoformat()
            daily_completed = conn.execute(
                "SELECT COUNT(DISTINCT challenge_id) FROM user_progress WHERE user_id = ? AND DATE(completed_at) = ?",
                (user_id, today),
            ).fetchone()[0]
            if daily_completed >= requirement_value and db_queries.award_badge(conn, user_id, badge["id"]):
                new_badges.append(dict(badge))

    conn.close()
    return new_badges


def get_unlocked_challenges(challenges, completed_ids):
    """Determine which challenges are unlocked (linear progression)."""
    unlocked = []
    for i, challenge in enumerate(challenges):
        if i == 0 or challenges[i - 1]["id"] in completed_ids:
            unlocked.append(challenge["id"])
    return unlocked
