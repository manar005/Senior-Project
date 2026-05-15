"""
Sync challenge definitions from Python track order to the database.
Run this after editing any challenge metadata in challenges/__init__.py or category modules.

Usage: from project root:  python scripts/sync_challenges_to_db.py
"""
import os
import sys
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DATABASE = os.path.join(PROJECT_ROOT, "thaghrah.db")


def sync():
    from challenges import challenge_dict_for_db_id

    challenges = [challenge_dict_for_db_id(i) for i in range(1, 41)]
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    categories = conn.execute("SELECT id FROM challenge_categories").fetchall()
    valid_category_ids = {row["id"] for row in categories}
    default_cat_id = min(valid_category_ids) if valid_category_ids else None
    updated = 0
    for i, c in enumerate(challenges, start=1):
        category_id = c.get("category_id", default_cat_id)
        if category_id not in valid_category_ids:
            category_id = default_cat_id
        order_in_cat = c.get("order_in_category", 1)
        if category_id is not None:
            cur = conn.execute(
                """
                UPDATE challenges
                SET title = ?, description = ?, hint = ?, flag = ?, expected_outcome = ?,
                    challenge_type = ?, order_in_category = ?, category_id = ?, points = ?
                WHERE id = ?
                """,
                (
                    c["title"],
                    c["description"],
                    c["hint"],
                    c["flag"],
                    c["expected_outcome"],
                    c["challenge_type"],
                    order_in_cat,
                    category_id,
                    c.get("points", 100),
                    i,
                ),
            )
        else:
            cur = conn.execute(
                """
                UPDATE challenges
                SET title = ?, description = ?, hint = ?, flag = ?, expected_outcome = ?,
                    challenge_type = ?, order_in_category = ?, points = ?
                WHERE id = ?
                """,
                (
                    c["title"],
                    c["description"],
                    c["hint"],
                    c["flag"],
                    c["expected_outcome"],
                    c["challenge_type"],
                    order_in_cat,
                    c.get("points", 100),
                    i,
                ),
            )
        if cur.rowcount > 0:
            updated += 1
        else:
            cat_id = category_id if category_id is not None else default_cat_id
            if cat_id is not None:
                conn.execute(
                    """
                    INSERT INTO challenges (id, category_id, title, description, hint, flag,
                        expected_outcome, challenge_type, order_in_category, points)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        i,
                        cat_id,
                        c["title"],
                        c["description"],
                        c["hint"],
                        c["flag"],
                        c["expected_outcome"],
                        c["challenge_type"],
                        order_in_cat,
                        c.get("points", 100),
                    ),
                )
                updated += 1
    conn.commit()
    conn.close()
    return updated, len(challenges)


if __name__ == "__main__":
    try:
        updated, total = sync()
        print(f"Synced {updated}/{total} challenges from Python track order to database.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
