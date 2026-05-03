"""
Sync challenge definitions from Python files (challenges/<category>/challenge_XX.py) to the database.
Run this after editing any challenge's title, description, hint, flag, expected_outcome,
challenge_type, challenge_data, category_slug, or order_in_category.

Usage: from project root:  python scripts/sync_challenges_to_db.py
"""
import os
import sys
import sqlite3
import importlib

# Run from project root so we can import challenges
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def load_challenges_from_source():
    """
    Load all challenge dicts fresh from the Python source files.

    This clears cached modules and .pyc files under challenges/, invalidates
    import caches, and then imports challenges.get_network_challenges().
    """
    # Clear cached challenge modules so we always load fresh from .py
    for name in list(sys.modules.keys()):
        if name == 'challenges' or name.startswith('challenges.'):
            del sys.modules[name]

    # Remove challenge .pyc files so Python recompiles from current .py
    challenges_dir = os.path.join(PROJECT_ROOT, 'challenges')
    for root, _dirs, files in os.walk(challenges_dir):
        if '__pycache__' in root:
            for f in files:
                if f.endswith('.pyc'):
                    try:
                        os.remove(os.path.join(root, f))
                    except OSError:
                        pass

    importlib.invalidate_caches()
    from challenges import get_network_challenges

    return get_network_challenges()


DATABASE = os.path.join(PROJECT_ROOT, 'thaghrah.db')

# Map challenge category_slug to challenge_categories.title
SLUG_TO_TITLE = {
    'http': 'HTTP', 'tcp': 'TCP', 'dns': 'DNS', 'ftp': 'FTP',
    'icmp': 'ICMP', 'smtp': 'SMTP', 'tls': 'TLS', 'forensics': 'Forensics',
}

# Order must match challenges.get_network_challenges() so row ids 1..N align with pcap links and init_db.
CHALLENGE_FILE_ORDER = [
    ('http', 'challenge_01'),
    ('tcp', 'challenge_02'),
    ('dns', 'challenge_03'),
    ('ftp', 'challenge_04'),
    ('icmp', 'challenge_05'),
    ('smtp', 'challenge_06'),
    ('tcp', 'challenge_07'),
    ('tcp', 'challenge_08'),
    ('tcp', 'challenge_09'),
    ('tcp', 'challenge_17'),
    ('tls', 'challenge_16'),
    ('forensics', 'challenge_10'),
    ('forensics', 'challenge_11'),
    ('http', 'challenge_12'),
    ('http', 'challenge_13'),
    ('http', 'challenge_14'),
    ('http', 'challenge_15'),
    ('dns', 'challenge_18'),
    ('dns', 'challenge_19'),
    ('dns', 'challenge_20'),
    ('dns', 'challenge_21'),
    ('ftp', 'challenge_22'),
    ('ftp', 'challenge_23'),
    ('ftp', 'challenge_24'),
    ('ftp', 'challenge_25'),
    ('icmp', 'challenge_26'),
    ('icmp', 'challenge_27'),
    ('icmp', 'challenge_28'),
    ('icmp', 'challenge_29'),
    ('smtp', 'challenge_30'),
    ('smtp', 'challenge_31'),
    ('smtp', 'challenge_32'),
    ('smtp', 'challenge_33'),
    ('tls', 'challenge_34'),
    ('tls', 'challenge_35'),
    ('tls', 'challenge_36'),
    ('tls', 'challenge_37'),
    ('forensics', 'challenge_38'),
    ('forensics', 'challenge_39'),
    ('forensics', 'challenge_40'),
]


def load_challenges_from_disk():
    """
    Load every challenge dict by reading the .py file from disk and exec'ing it.
    This guarantees the DB is updated from the actual file contents, not cached imports.
    """
    challenges = []
    for category, module_name in CHALLENGE_FILE_ORDER:
        path = os.path.join(PROJECT_ROOT, 'challenges', category, module_name + '.py')
        if not os.path.isfile(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            ns = {}
            exec(compile(f.read(), path, 'exec'), ns)
        c = ns.get('challenge')
        if c and isinstance(c, dict):
            challenges.append(c)
    return challenges


def sync():
    # Prefer disk so any saved edit is reflected regardless of .pyc/import cache
    challenges = load_challenges_from_disk()
    if not challenges:
        challenges = load_challenges_from_source()
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    categories = conn.execute('SELECT id, title FROM challenge_categories').fetchall()
    title_to_id = {row['title']: row['id'] for row in categories}
    updated = 0
    for i, c in enumerate(challenges, start=1):
        category_title = SLUG_TO_TITLE.get(c.get('category_slug', 'http'), 'HTTP')
        category_id = title_to_id.get(category_title)
        order_in_cat = c.get('order_in_category', 1)
        if category_id is not None:
            cur = conn.execute('''
                UPDATE challenges
                SET title = ?, description = ?, hint = ?, flag = ?, expected_outcome = ?,
                    challenge_type = ?, challenge_data = ?, order_num = ?, category_id = ?, points = ?
                WHERE id = ?
            ''', (
                c['title'], c['description'], c['hint'], c['flag'], c['expected_outcome'],
                c['challenge_type'], c.get('challenge_data'), order_in_cat, category_id, c.get('points', 100), i
            ))
        else:
            cur = conn.execute('''
                UPDATE challenges
                SET title = ?, description = ?, hint = ?, flag = ?, expected_outcome = ?,
                    challenge_type = ?, challenge_data = ?, order_num = ?, points = ?
                WHERE id = ?
            ''', (
                c['title'], c['description'], c['hint'], c['flag'], c['expected_outcome'],
                c['challenge_type'], c.get('challenge_data'), order_in_cat, c.get('points', 100), i
            ))
        if cur.rowcount > 0:
            updated += 1
        else:
            # New challenge row: INSERT so sync adds challenges 12, 13, ...
            cat_id = category_id if category_id is not None else (list(title_to_id.values())[0] if title_to_id else None)
            if cat_id is not None:
                conn.execute('''
                    INSERT INTO challenges (id, category_id, title, description, hint, flag,
                        expected_outcome, challenge_type, challenge_data, order_num, points)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (i, cat_id, c['title'], c['description'], c['hint'], c['flag'], c['expected_outcome'],
                      c['challenge_type'], c.get('challenge_data'), order_in_cat, c.get('points', 100)))
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
