"""
Sync challenge definitions from Python files (challenges/<category>/challenge_XX.py) to the database.
Run this after editing any challenge's title, description, hint, flag, expected_outcome,
challenge_type, category_id, order_in_category, etc.

Usage: from project root:  python scripts/sync_challenges_to_db.py
"""
import glob
import os
import sys
import sqlite3

# Run from project root so we can import challenges
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DATABASE = os.path.join(PROJECT_ROOT, 'thaghrah.db')


def load_challenge_from_disk_for_db_id(db_id: int):
    """
    Load the challenge dict for ``challenges.id == db_id``.

    Rows follow ``CHALLENGE_PCAP_SUFFIXES``: DB id maps to static ``challenge_%02d`` → one source file.
    """
    from challenges import CHALLENGE_PCAP_SUFFIXES

    suffix = CHALLENGE_PCAP_SUFFIXES[db_id - 1]
    pattern = os.path.join(PROJECT_ROOT, 'challenges', '*', f'challenge_{suffix:02d}.py')
    paths = sorted(glob.glob(pattern))
    if len(paths) != 1:
        raise RuntimeError(
            f"expected exactly one challenges/*/challenge_{suffix:02d}.py for DB id {db_id}, got {paths!r}"
        )
    path = paths[0]
    with open(path, 'r', encoding='utf-8') as f:
        ns = {}
        exec(compile(f.read(), path, 'exec'), ns)
    c = ns.get('challenge')
    if not isinstance(c, dict):
        raise RuntimeError(f"no challenge dict in {path}")
    return c


def load_all_challenges_from_disk_by_db_id():
    return [load_challenge_from_disk_for_db_id(i) for i in range(1, 41)]


def sync():
    # Disk load order matches DB primary keys 1..40 (via CHALLENGE_PCAP_SUFFIXES).
    try:
        challenges = load_all_challenges_from_disk_by_db_id()
    except (RuntimeError, OSError) as e:
        print(f"Disk load failed ({e}); using imported challenge dicts.", file=sys.stderr)
        from challenges import challenge_dict_for_db_id

        challenges = [challenge_dict_for_db_id(i) for i in range(1, 41)]
    if not challenges:
        from challenges import challenge_dict_for_db_id

        challenges = [challenge_dict_for_db_id(i) for i in range(1, 41)]
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    categories = conn.execute('SELECT id FROM challenge_categories').fetchall()
    valid_category_ids = {row['id'] for row in categories}
    default_cat_id = min(valid_category_ids) if valid_category_ids else None
    updated = 0
    for i, c in enumerate(challenges, start=1):
        category_id = c.get('category_id', default_cat_id)
        if category_id not in valid_category_ids:
            category_id = default_cat_id
        order_in_cat = c.get('order_in_category', 1)
        if category_id is not None:
            cur = conn.execute('''
                UPDATE challenges
                SET title = ?, description = ?, hint = ?, flag = ?, expected_outcome = ?,
                    challenge_type = ?, order_in_category = ?, category_id = ?, points = ?
                WHERE id = ?
            ''', (
                c['title'], c['description'], c['hint'], c['flag'], c['expected_outcome'],
                c['challenge_type'], order_in_cat, category_id, c.get('points', 100), i
            ))
        else:
            cur = conn.execute('''
                UPDATE challenges
                SET title = ?, description = ?, hint = ?, flag = ?, expected_outcome = ?,
                    challenge_type = ?, order_in_category = ?, points = ?
                WHERE id = ?
            ''', (
                c['title'], c['description'], c['hint'], c['flag'], c['expected_outcome'],
                c['challenge_type'], order_in_cat, c.get('points', 100), i
            ))
        if cur.rowcount > 0:
            updated += 1
        else:
            # New challenge row: INSERT so sync adds challenges 12, 13, ...
            cat_id = category_id if category_id is not None else default_cat_id
            if cat_id is not None:
                conn.execute('''
                    INSERT INTO challenges (id, category_id, title, description, hint, flag,
                        expected_outcome, challenge_type, order_in_category, points)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (i, cat_id, c['title'], c['description'], c['hint'], c['flag'], c['expected_outcome'],
                      c['challenge_type'], order_in_cat, c.get('points', 100)))
                updated += 1
    conn.commit()
    conn.close()
    return updated, len(challenges)

if __name__ == '__main__':
    try:
        updated, total = sync()
        print(f'Synced {updated}/{total} challenges from Python files to database.')
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
