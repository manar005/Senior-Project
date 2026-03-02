"""One-off helper to insert challenge 11 (HTTP Login Brute Force) into the database.
Run from project root:  python scripts/add_challenge_11_to_db.py
"""
import os
import sys
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "thaghrah.db")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from challenges import get_network_challenges


def main():
    challenges = get_network_challenges()
    if len(challenges) < 11:
        raise SystemExit("Expected at least 11 challenges in get_network_challenges().")

    ch11 = challenges[10]  # index 10 -> id 11

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if id 11 already exists
    row = cur.execute("SELECT id FROM challenges WHERE id = ?", (11,)).fetchone()
    if row:
        print("Challenge with id 11 already exists; nothing to insert.")
        conn.close()
        return

    # Find category_id for Forensics (title stored in challenge_categories)
    cat = cur.execute(
        "SELECT id FROM challenge_categories WHERE title = ?", ("Forensics",)
    ).fetchone()
    if not cat:
        conn.close()
        raise SystemExit("Could not find 'Forensics' category in challenge_categories.")

    category_id = cat[0]
    order_in_cat = ch11.get("order_in_category", 2)
    points = ch11.get("points", 100)

    cur.execute(
        """
        INSERT INTO challenges
        (id, category_id, title, description, hint, flag, expected_outcome,
         challenge_type, challenge_data, order_num, points)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            11,
            category_id,
            ch11["title"],
            ch11["description"],
            ch11["hint"],
            ch11["flag"],
            ch11["expected_outcome"],
            ch11["challenge_type"],
            ch11.get("challenge_data"),
            order_in_cat,
            points,
        ),
    )

    conn.commit()
    conn.close()
    print("Inserted challenge 11 into database.")


if __name__ == "__main__":
    main()

