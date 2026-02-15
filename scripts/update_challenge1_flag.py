"""One-time script: update challenge 1 flag in DB to match challenge_01.py."""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'thaghrah.db')
conn = sqlite3.connect(db_path)
conn.execute("UPDATE challenges SET flag = ? WHERE id = 1", ('NETWORK_HTTP_FLAG',))
conn.commit()
print("Updated challenge 1 flag to NETWORK_HTTP_FLAG")
conn.close()
