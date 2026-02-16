"""
Sync challenge definitions from Python files (challenges/challenge_XX.py) to the database.
Run this after editing any challenge's title, description, hint, flag, expected_outcome,
challenge_type, challenge_data, or order_num so the app shows the updated values.

Usage: from project root:  python scripts/sync_challenges_to_db.py
"""
import os
import sys
import sqlite3

# Run from project root so we can import challenges
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from challenges import get_network_challenges

DATABASE = os.path.join(PROJECT_ROOT, 'thaghrah.db')

def sync():
    challenges = get_network_challenges()
    conn = sqlite3.connect(DATABASE)
    updated = 0
    for i, c in enumerate(challenges, start=1):
        cur = conn.execute('''
            UPDATE challenges
            SET title = ?, description = ?, hint = ?, flag = ?, expected_outcome = ?,
                challenge_type = ?, challenge_data = ?, order_num = ?
            WHERE id = ?
        ''', (
            c['title'],
            c['description'],
            c['hint'],
            c['flag'],
            c['expected_outcome'],
            c['challenge_type'],
            c.get('challenge_data'),
            c.get('order_num', i),
            i,
        ))
        if cur.rowcount > 0:
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
