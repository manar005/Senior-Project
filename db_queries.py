"""
Database query helper functions
This module contains reusable database query functions using conn.execute() instead of cursor.execute()
"""
import sqlite3

def get_user_by_email(conn, email):
    """Get user by email"""
    return conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

def create_user(conn, name, email, password_hash):
    """Create a new user"""
    result = conn.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', 
                   (name, email, password_hash))
    conn.commit()
    return result.lastrowid

def get_all_challenges(conn):
    """Get all challenges ordered by order_num"""
    return conn.execute('SELECT * FROM challenges ORDER BY order_num').fetchall()

def get_challenge_by_id(conn, challenge_id):
    """Get challenge by ID"""
    return conn.execute('SELECT * FROM challenges WHERE id = ?', (challenge_id,)).fetchone()

def get_user_progress(conn, user_id):
    """Get user's completed challenges"""
    return conn.execute('SELECT challenge_id FROM user_progress WHERE user_id = ?', 
                         (user_id,)).fetchall()

def check_challenge_completed(conn, user_id, challenge_id):
    """Check if user has completed a challenge"""
    return conn.execute('SELECT * FROM user_progress WHERE user_id = ? AND challenge_id = ?',
                         (user_id, challenge_id)).fetchone()

def complete_challenge(conn, user_id, challenge_id):
    """Mark challenge as completed for user
    Returns True if challenge was marked as completed, False if already completed"""
    # Check if already completed to prevent duplicates
    existing = check_challenge_completed(conn, user_id, challenge_id)
    if not existing:
        conn.execute('INSERT INTO user_progress (user_id, challenge_id) VALUES (?, ?)',
                       (user_id, challenge_id))
        conn.commit()
        return True
    return False

def get_user_badges(conn, user_id):
    """Get user's earned badges"""
    return conn.execute('''
        SELECT b.id, b.name, b.description, b.icon, ub.earned_at
        FROM badges b
        INNER JOIN user_badges ub ON b.id = ub.badge_id
        WHERE ub.user_id = ?
        ORDER BY ub.earned_at DESC
    ''', (user_id,)).fetchall()

def get_total_badges_count(conn):
    """Get total number of badges"""
    result = conn.execute('SELECT COUNT(*) FROM badges').fetchone()
    return result[0] if result else 0

def get_user_badge_ids(conn, user_id):
    """Get list of badge IDs earned by user"""
    results = conn.execute('SELECT badge_id FROM user_badges WHERE user_id = ?', 
                            (user_id,)).fetchall()
    return [row[0] for row in results]

def award_badge(conn, user_id, badge_id):
    """Award a badge to a user (only if not already awarded)
    Returns True if badge was awarded, False if already exists"""
    # Check if badge already exists to prevent duplicates
    existing = conn.execute('SELECT * FROM user_badges WHERE user_id = ? AND badge_id = ?',
                           (user_id, badge_id)).fetchone()
    if not existing:
        conn.execute('INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)',
                     (user_id, badge_id))
        conn.commit()
        return True
    return False

def get_all_badges(conn):
    """Get all badge definitions"""
    return conn.execute('SELECT * FROM badges').fetchall()

def get_challenge_count(conn):
    """Get total number of challenges"""
    result = conn.execute('SELECT COUNT(*) FROM challenges').fetchone()
    return result[0] if result else 0

def get_badge_count(conn):
    """Get total number of badges"""
    result = conn.execute('SELECT COUNT(*) FROM badges').fetchone()
    return result[0] if result else 0

def insert_challenges(conn, challenge_data_list):
    """Insert multiple challenges using batch insert"""
    conn.executemany('''
        INSERT INTO challenges (title, description, hint, flag, expected_outcome, challenge_type, challenge_data, order_num)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', challenge_data_list)
    conn.commit()
