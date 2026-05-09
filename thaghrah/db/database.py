"""SQLite connection and schema initialization."""
import os
import sqlite3

from challenges import challenge_dict_for_db_id, get_network_challenges
from thaghrah.core.config import APP_ROOT, DATABASE
from thaghrah.core.constants import PROTOCOL_NAMES
from thaghrah.db import queries as db_queries


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def reconcile_network_challenge_categories(conn):
    """
    Align challenges.category_id and order_in_category with Python definitions.

    Intended for incremental fixes; full challenge metadata sync can be run via
    ``scripts/sync_challenges_to_db.py``.
    """
    if db_queries.get_challenge_count(conn) == 0:
        return
    categories = db_queries.get_all_categories(conn)
    valid_category_ids = {c["id"] for c in categories}
    rows = conn.execute("SELECT id FROM challenges ORDER BY id").fetchall()
    for row in rows:
        try:
            ch = challenge_dict_for_db_id(row["id"])
        except ValueError:
            continue
        if not ch:
            continue
        category_id = ch.get("category_id")
        if category_id not in valid_category_ids:
            continue
        order_in_cat = ch.get("order_in_category", 1)
        conn.execute(
            "UPDATE challenges SET category_id = ?, order_in_category = ? WHERE id = ?",
            (category_id, order_in_cat, row["id"]),
        )
    conn.commit()


def init_db():
    """Apply schema from ``schema.sql``, seed defaults, reconcile challenge categories."""
    conn = get_db()

    schema_path = os.path.join(APP_ROOT, "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

    if db_queries.get_category_count(conn) == 0:
        db_queries.insert_categories(conn, [(name,) for name in PROTOCOL_NAMES])
        conn.commit()
    elif db_queries.get_category_count(conn) == 8:
        try:
            for idx, name in enumerate(PROTOCOL_NAMES, start=1):
                conn.execute(
                    "UPDATE challenge_categories SET title = ? WHERE id = ?",
                    (name, idx),
                )
            conn.commit()
        except sqlite3.OperationalError:
            pass

    total_challenges = len(get_network_challenges())

    def pct_threshold(pct):
        return max(1, round(total_challenges * pct))

    completion_thresholds = [
        1,
        pct_threshold(0.25),
        pct_threshold(0.50),
        pct_threshold(0.75),
        total_challenges,
    ]
    for i in range(1, len(completion_thresholds)):
        if completion_thresholds[i] <= completion_thresholds[i - 1]:
            completion_thresholds[i] = completion_thresholds[i - 1] + 1
    completion_thresholds[-1] = total_challenges

    badges_data = [
        ("First Steps", "Complete your first network challenge", "🎯", "challenges_completed", completion_thresholds[0]),
        ("Getting Started", f"Complete {completion_thresholds[1]} network challenges", "🌟", "challenges_completed", completion_thresholds[1]),
        ("Halfway Hero", f"Complete {completion_thresholds[2]} network challenges", "🏆", "challenges_completed", completion_thresholds[2]),
        ("Network Expert", f"Complete {completion_thresholds[3]} network challenges", "💎", "challenges_completed", completion_thresholds[3]),
        ("Network Master", f"Complete all {total_challenges} network challenges", "🏅", "challenges_completed", completion_thresholds[4]),
        ("Quick Learner", "Complete 3 challenges in one day", "⚡", "daily_challenges", 3),
        ("Dedicated", "Complete 5 challenges in one day", "🔥", "daily_challenges", 5),
    ]

    for badge in badges_data:
        existing = conn.execute("SELECT id FROM badges WHERE name = ?", (badge[0],)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE badges
                SET description = ?, icon = ?, requirement_type = ?, requirement_value = ?
                WHERE id = ?
                """,
                (badge[1], badge[2], badge[3], badge[4], existing["id"]),
            )
        else:
            conn.execute(
                """
                INSERT INTO badges (name, description, icon, requirement_type, requirement_value)
                VALUES (?, ?, ?, ?, ?)
                """,
                badge,
            )
    conn.commit()

    if db_queries.get_challenge_count(conn) == 0:
        network_challenges = get_network_challenges()
        categories = db_queries.get_all_categories(conn)
        valid_category_ids = {c["id"] for c in categories}
        default_cat_id = min(valid_category_ids) if valid_category_ids else 1
        challenge_rows = []
        for c in network_challenges:
            category_id = c.get("category_id", default_cat_id)
            if category_id not in valid_category_ids:
                category_id = default_cat_id
            order_in_cat = c.get("order_in_category", 1)
            challenge_rows.append(
                (
                    category_id,
                    c["title"],
                    c["description"],
                    c["hint"],
                    c["flag"],
                    c["expected_outcome"],
                    c["challenge_type"],
                    order_in_cat,
                    c.get("points", 100),
                )
            )
        db_queries.insert_challenges(conn, challenge_rows)

    reconcile_network_challenge_categories(conn)
    conn.close()
