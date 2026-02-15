"""
Sync challenge content from Python files (challenges/challenge_XX.py) to the database.
Run this after editing any challenge so the browser shows your changes.

Usage: python scripts/sync_challenges_to_db.py
"""
import os
import sys
import sqlite3

# Add project root so we can import challenges
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from challenges import get_network_challenges

db_path = os.path.join(os.path.dirname(__file__), '..', 'thaghrah.db')
conn = sqlite3.connect(db_path)

challenges = get_network_challenges()
for idx, ch in enumerate(challenges, start=1):
    conn.execute('''
        UPDATE challenges
        SET title = ?, description = ?, hint = ?, flag = ?, expected_outcome = ?, challenge_type = ?, challenge_data = ?
        WHERE id = ?
    ''', (
        ch['title'],
        ch['description'],
        ch['hint'],
        ch['flag'],
        ch['expected_outcome'],
        ch['challenge_type'],
        ch.get('challenge_data'),
        idx
    ))

conn.commit()
print(f"Synced {len(challenges)} challenge(s) from Python files to the database.")
conn.close()
