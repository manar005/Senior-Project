"""SQLite connection and schema initialization."""
import os
import sqlite3

import db_queries
from ai_challenge_utils import extract_flag_inner_value
from challenges import get_network_challenges

from thaghrah.config import APP_ROOT, DATABASE
from thaghrah.constants import PROTOCOL_NAMES


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def _migrate_challenge_categories_drop_order_num(conn):
    """
    Remove legacy challenge_categories.order_num; UI/query order uses id.
    Preserves id and title. Runs legacy NULL category_id backfill while order_num still exists.
    """
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(challenge_categories)").fetchall()]
    except sqlite3.OperationalError:
        return
    if "order_num" not in cols:
        return
    try:
        conn.execute(
            """
            UPDATE challenges SET category_id = (
                SELECT cc.id FROM challenge_categories cc
                WHERE cc.order_num = challenges.order_in_category
            ) WHERE category_id IS NULL
            """
        )
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE challenge_categories DROP COLUMN order_num")
        conn.commit()
        return
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("PRAGMA foreign_keys=OFF")
        conn.execute("BEGIN")
        conn.execute(
            """
            CREATE TABLE challenge_categories__rebuilt (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT INTO challenge_categories__rebuilt (id, title) SELECT id, title FROM challenge_categories"
        )
        conn.execute("DROP TABLE challenge_categories")
        conn.execute("ALTER TABLE challenge_categories__rebuilt RENAME TO challenge_categories")
        conn.execute("COMMIT")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.commit()
    except sqlite3.OperationalError:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("PRAGMA foreign_keys=ON")
            conn.commit()
        except sqlite3.OperationalError:
            pass


def _legacy_challenge_id_shuffle_needed(conn):
    """True if DB still uses old global order (challenge_13 at id 15, etc.)."""
    try:
        row = conn.execute("SELECT title FROM challenges WHERE id = ?", (13,)).fetchone()
    except sqlite3.OperationalError:
        return False
    if not row:
        return False
    return (row["title"] or "") != "HTTP Request Method"


def _migrate_user_progress_challenge_ids_shuffle(conn):
    """Remap user_progress when challenge primary keys move to match challenge_NN (10..17 swap)."""
    conn.execute(
        """
        UPDATE user_progress SET challenge_id = CASE challenge_id
            WHEN 10 THEN 17
            WHEN 11 THEN 16
            WHEN 12 THEN 10
            WHEN 13 THEN 11
            WHEN 14 THEN 12
            WHEN 15 THEN 13
            WHEN 16 THEN 14
            WHEN 17 THEN 15
            ELSE challenge_id
        END
        WHERE challenge_id BETWEEN 10 AND 17
        """
    )
    conn.commit()


def _rewrite_network_challenges_from_python(conn):
    """Overwrite rows id 1..N from get_network_challenges() (titles, flags, category_id, etc.)."""
    network = get_network_challenges()
    for i, c in enumerate(network, start=1):
        conn.execute(
            """
            UPDATE challenges SET
                title = ?, description = ?, hint = ?, flag = ?, expected_outcome = ?,
                challenge_type = ?, challenge_data = ?, order_in_category = ?, category_id = ?, points = ?
            WHERE id = ?
            """,
            (
                c["title"],
                c["description"],
                c["hint"],
                c["flag"],
                c["expected_outcome"],
                c["challenge_type"],
                c.get("challenge_data"),
                c.get("order_in_category", 1),
                c.get("category_id", 1),
                c.get("points", 100),
                i,
            ),
        )
    conn.commit()


def reconcile_network_challenge_categories(conn):
    """
    Align challenges.category_id and order_in_category with Python definitions.
    Fixes stale migrations and keeps DB consistent with get_network_challenges() order.
    """
    if db_queries.get_challenge_count(conn) == 0:
        return
    network = get_network_challenges()
    by_id = {i + 1: ch for i, ch in enumerate(network)}
    categories = db_queries.get_all_categories(conn)
    valid_category_ids = {c["id"] for c in categories}
    rows = conn.execute("SELECT id FROM challenges ORDER BY id").fetchall()
    for row in rows:
        ch = by_id.get(row["id"])
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
    """Initialize database from schema.sql and run migrations."""
    conn = get_db()

    schema_path = os.path.join(APP_ROOT, "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

    # Rename legacy challenges.order_num → order_in_category (matches Python field name)
    try:
        ch_cols = [r[1] for r in conn.execute("PRAGMA table_info(challenges)").fetchall()]
        if "order_num" in ch_cols and "order_in_category" not in ch_cols:
            conn.execute("ALTER TABLE challenges RENAME COLUMN order_num TO order_in_category")
            conn.commit()
    except sqlite3.OperationalError:
        pass

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
                title TEXT NOT NULL
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
        category_data = [(name,) for name in PROTOCOL_NAMES]
        db_queries.insert_categories(conn, category_data)
        conn.commit()
    else:
        if db_queries.get_category_count(conn) == 8:
            for idx, name in enumerate(PROTOCOL_NAMES, start=1):
                try:
                    conn.execute(
                        "UPDATE challenge_categories SET title = ? WHERE id = ?",
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
                    "SELECT id, order_in_category FROM challenges WHERE category_id IN ({}) ORDER BY category_id, order_in_category".format(
                        ",".join("?" * len(extra_ids))
                    ),
                    extra_ids,
                )
                rows = cur.fetchall()
                for i, row in enumerate(rows):
                    conn.execute(
                        "UPDATE challenges SET category_id = ?, order_in_category = ? WHERE id = ?",
                        (tcp_id, i + 2, row["id"]),
                    )
                conn.commit()
                for cid in extra_ids:
                    conn.execute("DELETE FROM challenge_categories WHERE id = ?", (cid,))
                conn.commit()
                conn.execute("UPDATE challenges SET category_id = 9 WHERE id = 9")
                conn.execute("UPDATE challenges SET category_id = 10 WHERE id = 10")
                conn.commit()
            elif tcp_primary:
                tcp_id = tcp_primary["id"]
                for challenge_id, order_in_tcp in [(2, 1), (7, 2), (8, 3), (9, 4), (10, 5)]:
                    conn.execute(
                        "UPDATE challenges SET category_id = ?, order_in_category = ? WHERE id = ?",
                        (tcp_id, order_in_tcp, challenge_id),
                    )
                conn.commit()
        except (sqlite3.OperationalError, StopIteration):
            pass
    _migrate_challenge_categories_drop_order_num(conn)

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
        challenge_data = []
        for c in network_challenges:
            category_id = c.get("category_id", default_cat_id)
            if category_id not in valid_category_ids:
                category_id = default_cat_id
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

    if db_queries.get_challenge_count(conn) > 0 and _legacy_challenge_id_shuffle_needed(conn):
        _migrate_user_progress_challenge_ids_shuffle(conn)
        _rewrite_network_challenges_from_python(conn)

    reconcile_network_challenge_categories(conn)

    conn.close()
