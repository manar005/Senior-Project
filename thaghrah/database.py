"""SQLite connection and schema initialization."""
import os
import sqlite3

import db_queries
from ai_challenge_utils import extract_flag_inner_value
from challenges import get_network_challenges

from thaghrah.config import APP_ROOT, DATABASE
from thaghrah.constants import CATEGORY_SLUG_TO_ORDER, PROTOCOL_NAMES


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def reconcile_network_challenge_categories(conn):
    """
    Align challenges.category_id and order_num with Python definitions.
    Fixes stale migrations and keeps DB consistent with get_network_challenges() order.
    """
    if db_queries.get_challenge_count(conn) == 0:
        return
    network = get_network_challenges()
    by_id = {i + 1: ch for i, ch in enumerate(network)}
    categories = db_queries.get_all_categories(conn)
    by_order = {c["order_num"]: c["id"] for c in categories}
    rows = conn.execute("SELECT id FROM challenges ORDER BY id").fetchall()
    for row in rows:
        ch = by_id.get(row["id"])
        if not ch:
            continue
        cat_order = CATEGORY_SLUG_TO_ORDER.get(ch.get("category_slug"), 1)
        category_id = by_order.get(cat_order)
        if category_id is None:
            continue
        order_in_cat = ch.get("order_in_category", 1)
        conn.execute(
            "UPDATE challenges SET category_id = ?, order_num = ? WHERE id = ?",
            (category_id, order_in_cat, row["id"]),
        )
    conn.commit()


def init_db():
    """Initialize database from schema.sql and run migrations."""
    conn = get_db()

    schema_path = os.path.join(APP_ROOT, "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

    for sql in [
        "ALTER TABLE challenges ADD COLUMN points INTEGER NOT NULL DEFAULT 100",
        "ALTER TABLE user_progress ADD COLUMN used_hint INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE user_progress ADD COLUMN points_earned INTEGER NOT NULL DEFAULT 0",
    ]:
        try:
            conn.execute(sql)
            conn.commit()
        except sqlite3.OperationalError:
            pass

    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                code TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    except sqlite3.OperationalError:
        pass

    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                hint TEXT NOT NULL,
                outcome TEXT NOT NULL,
                points INTEGER NOT NULL DEFAULT 100,
                flag TEXT NOT NULL,
                display_flag TEXT,
                answer_flag TEXT,
                protocol TEXT,
                difficulty TEXT,
                pcap_path TEXT NOT NULL,
                original_prompt TEXT NOT NULL,
                hint_used INTEGER NOT NULL DEFAULT 0,
                completed INTEGER NOT NULL DEFAULT 0,
                awarded_points INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()
    except sqlite3.OperationalError:
        pass

    for sql in [
        "ALTER TABLE ai_challenges ADD COLUMN display_flag TEXT",
        "ALTER TABLE ai_challenges ADD COLUMN answer_flag TEXT",
    ]:
        try:
            conn.execute(sql)
            conn.commit()
        except sqlite3.OperationalError:
            pass
    try:
        rows = conn.execute("SELECT id, flag, display_flag, answer_flag FROM ai_challenges").fetchall()
        for row in rows:
            display_flag = row["display_flag"] if row["display_flag"] else row["flag"]
            answer_flag = row["answer_flag"] if row["answer_flag"] else extract_flag_inner_value(row["flag"])
            if not answer_flag:
                answer_flag = row["flag"]
            conn.execute(
                "UPDATE ai_challenges SET display_flag = ?, answer_flag = ? WHERE id = ?",
                (display_flag, answer_flag, row["id"]),
            )
        conn.commit()
    except sqlite3.OperationalError:
        pass

    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS challenge_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                order_num INTEGER NOT NULL
            )
            """
        )
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE challenges ADD COLUMN category_id INTEGER")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    if db_queries.get_category_count(conn) == 0:
        category_data = [(PROTOCOL_NAMES[idx], idx + 1) for idx in range(len(PROTOCOL_NAMES))]
        db_queries.insert_categories(conn, category_data)
        conn.commit()
    else:
        if db_queries.get_category_count(conn) == 8:
            for idx, name in enumerate(PROTOCOL_NAMES, start=1):
                try:
                    conn.execute(
                        "UPDATE challenge_categories SET title = ? WHERE order_num = ?",
                        (name, idx),
                    )
                    conn.commit()
                except sqlite3.OperationalError:
                    pass
        try:
            categories = db_queries.get_all_categories(conn)
            tcp_primary = next((c for c in categories if c["title"] == "TCP"), None)
            tcp_extra = [c for c in categories if c["title"] in ("TCP Handshake Count", "TCP Fragmentation")]
            if tcp_primary and tcp_extra:
                tcp_id = tcp_primary["id"]
                extra_ids = [c["id"] for c in tcp_extra]
                cur = conn.execute(
                    "SELECT id, order_num FROM challenges WHERE category_id IN ({}) ORDER BY category_id, order_num".format(
                        ",".join("?" * len(extra_ids))
                    ),
                    extra_ids,
                )
                rows = cur.fetchall()
                for i, row in enumerate(rows):
                    conn.execute(
                        "UPDATE challenges SET category_id = ?, order_num = ? WHERE id = ?",
                        (tcp_id, i + 2, row["id"]),
                    )
                conn.commit()
                for cid in extra_ids:
                    conn.execute("DELETE FROM challenge_categories WHERE id = ?", (cid,))
                conn.commit()
                conn.execute("UPDATE challenge_categories SET order_num = 7 WHERE order_num = 9")
                conn.execute("UPDATE challenge_categories SET order_num = 8 WHERE order_num = 10")
                conn.commit()
                conn.execute("UPDATE challenges SET category_id = 9 WHERE id = 9")
                conn.execute("UPDATE challenges SET category_id = 10 WHERE id = 10")
                conn.commit()
            elif tcp_primary:
                tcp_id = tcp_primary["id"]
                for challenge_id, order_in_tcp in [(2, 1), (7, 2), (8, 3), (9, 4), (10, 5)]:
                    conn.execute(
                        "UPDATE challenges SET category_id = ?, order_num = ? WHERE id = ?",
                        (tcp_id, order_in_tcp, challenge_id),
                    )
                conn.commit()
        except (sqlite3.OperationalError, StopIteration):
            pass
    try:
        conn.execute(
            """
            UPDATE challenges SET category_id = (
                SELECT id FROM challenge_categories WHERE challenge_categories.order_num = challenges.order_num
            ) WHERE category_id IS NULL
            """
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
        by_order = {c["order_num"]: c["id"] for c in categories}
        challenge_data = []
        for c in network_challenges:
            cat_order = CATEGORY_SLUG_TO_ORDER.get(c.get("category_slug"), 1)
            category_id = by_order.get(cat_order, list(by_order.values())[0])
            order_in_cat = c.get("order_in_category", 1)
            challenge_data.append(
                (
                    category_id,
                    c["title"],
                    c["description"],
                    c["hint"],
                    c["flag"],
                    c["expected_outcome"],
                    c["challenge_type"],
                    c.get("challenge_data"),
                    order_in_cat,
                    c.get("points", 100),
                )
            )
        db_queries.insert_challenges(conn, challenge_data)

    reconcile_network_challenge_categories(conn)

    conn.close()
