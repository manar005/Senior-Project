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
    """Get all challenges ordered by category order_num then challenge order_num"""
    return conn.execute('''
        SELECT c.* FROM challenges c
        JOIN challenge_categories cc ON c.category_id = cc.id
        ORDER BY cc.order_num, c.order_num
    ''').fetchall()

def get_all_categories(conn):
    """Get all categories ordered by order_num"""
    return conn.execute('SELECT * FROM challenge_categories ORDER BY order_num').fetchall()

def get_category_by_id(conn, category_id):
    """Get a single category by id"""
    return conn.execute('SELECT * FROM challenge_categories WHERE id = ?', (category_id,)).fetchone()

def get_challenges_by_category(conn, category_id):
    """Get challenges in a category ordered by order_num"""
    return conn.execute(
        'SELECT * FROM challenges WHERE category_id = ? ORDER BY order_num',
        (category_id,)
    ).fetchall()

def get_challenges_by_category_ids(conn, category_ids):
    """Get challenges in any of the given categories, ordered by category order_num then challenge order_num"""
    if not category_ids:
        return []
    placeholders = ','.join('?' * len(category_ids))
    return conn.execute('''
        SELECT c.* FROM challenges c
        JOIN challenge_categories cc ON c.category_id = cc.id
        WHERE c.category_id IN ({})
        ORDER BY cc.order_num, c.order_num
    '''.format(placeholders), category_ids).fetchall()

def get_all_challenges_ordered(conn):
    """Get all challenges in global order (for unlock logic). Same as get_all_challenges."""
    return get_all_challenges(conn)

def get_challenge_by_id(conn, challenge_id):
    """Get challenge by ID"""
    return conn.execute('SELECT * FROM challenges WHERE id = ?', (challenge_id,)).fetchone()

def get_user_progress(conn, user_id):
    """Get user's completed challenges (challenge_id, points_earned, used_hint)"""
    return conn.execute(
        'SELECT challenge_id, points_earned, used_hint FROM user_progress WHERE user_id = ?',
        (user_id,)
    ).fetchall()

def check_challenge_completed(conn, user_id, challenge_id):
    """Check if user has completed a challenge"""
    return conn.execute('SELECT * FROM user_progress WHERE user_id = ? AND challenge_id = ?',
                         (user_id, challenge_id)).fetchone()

def complete_challenge(conn, user_id, challenge_id, used_hint=False, points_earned=0):
    """Mark challenge as completed for user with optional hint usage and points earned.
    Returns True if challenge was marked as completed, False if already completed"""
    existing = check_challenge_completed(conn, user_id, challenge_id)
    if not existing:
        conn.execute(
            'INSERT INTO user_progress (user_id, challenge_id, used_hint, points_earned) VALUES (?, ?, ?, ?)',
            (user_id, challenge_id, 1 if used_hint else 0, points_earned)
        )
        conn.commit()
        return True
    return False

def get_user_total_points(conn, user_id):
    """Get total points earned by user (network challenges + completed AI challenges)."""
    row = conn.execute('SELECT COALESCE(SUM(points_earned), 0) FROM user_progress WHERE user_id = ?', (user_id,)).fetchone()
    base = row[0] if row else 0
    try:
        ai_row = conn.execute(
            'SELECT COALESCE(SUM(awarded_points), 0) FROM ai_challenges WHERE user_id = ? AND completed = 1',
            (user_id,),
        ).fetchone()
        base += ai_row[0] if ai_row else 0
    except sqlite3.OperationalError:
        pass
    return base


# --- AI-generated challenges ---


def insert_ai_challenge(
    conn,
    user_id,
    title,
    description,
    hint,
    outcome,
    points,
    display_flag,
    answer_flag,
    protocol,
    difficulty,
    pcap_path,
    original_prompt,
):
    """Insert a new AI challenge row. Returns new row id."""
    cur = conn.execute(
        '''
        INSERT INTO ai_challenges (
            user_id, title, description, hint, outcome, points, flag, display_flag, answer_flag,
            protocol, difficulty, pcap_path, original_prompt,
            hint_used, completed, awarded_points
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
        ''',
        (
            user_id,
            title,
            description,
            hint,
            outcome,
            points,
            display_flag,
            display_flag,
            answer_flag,
            protocol,
            difficulty,
            pcap_path,
            original_prompt,
        ),
    )
    conn.commit()
    return cur.lastrowid


def get_ai_challenge_for_user(conn, ai_id, user_id):
    """Return ai_challenges row if it belongs to user."""
    return conn.execute(
        'SELECT * FROM ai_challenges WHERE id = ? AND user_id = ?',
        (ai_id, user_id),
    ).fetchone()


def mark_ai_challenge_hint_used(conn, ai_id, user_id):
    """Set hint_used=1 for an incomplete challenge owned by user."""
    conn.execute(
        'UPDATE ai_challenges SET hint_used = 1 WHERE id = ? AND user_id = ? AND completed = 0',
        (ai_id, user_id),
    )
    conn.commit()


def complete_ai_challenge(conn, user_id, ai_id, awarded_points):
    """
    Mark AI challenge completed with awarded points. No-op if already completed.
    Returns True if a row was updated.
    """
    cur = conn.execute(
        '''
        UPDATE ai_challenges SET completed = 1, awarded_points = ?
        WHERE id = ? AND user_id = ? AND completed = 0
        ''',
        (awarded_points, ai_id, user_id),
    )
    conn.commit()
    return cur.rowcount > 0


def list_ai_challenges_for_user(conn, user_id, limit=50):
    """Recent AI challenges for dashboard/history (optional)."""
    return conn.execute(
        '''
        SELECT id, title, protocol, difficulty, points, completed, awarded_points, hint_used, created_at
        FROM ai_challenges WHERE user_id = ? ORDER BY id DESC LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()

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
    """Total number of challenges"""
    result = conn.execute('SELECT COUNT(*) FROM challenges').fetchone()
    return result[0] if result else 0

def get_category_count(conn):
    """Total number of categories"""
    result = conn.execute('SELECT COUNT(*) FROM challenge_categories').fetchone()
    return result[0] if result else 0

def insert_categories(conn, category_data_list):
    """Insert category rows. Each item: (title, order_num)"""
    conn.executemany(
        'INSERT INTO challenge_categories (title, order_num) VALUES (?, ?)',
        category_data_list
    )
    conn.commit()

def insert_challenges(conn, challenge_data_list):
    """Insert challenges. Each item: (category_id, title, description, hint, flag, expected_outcome, challenge_type, challenge_data, order_num, points)"""
    conn.executemany('''
        INSERT INTO challenges (category_id, title, description, hint, flag, expected_outcome, challenge_type, challenge_data, order_num, points)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', challenge_data_list)
    conn.commit()

def get_badge_count(conn):
    """Get total number of badges"""
    result = conn.execute('SELECT COUNT(*) FROM badges').fetchone()
    return result[0] if result else 0

# --- Password reset ---

def create_reset_code(conn, email, code, expires_at):
    """Store a password reset code for the given email. Replaces any existing code for this email."""
    conn.execute('DELETE FROM password_reset_codes WHERE email = ?', (email,))
    conn.execute(
        'INSERT INTO password_reset_codes (email, code, expires_at) VALUES (?, ?, ?)',
        (email, code, expires_at)
    )
    conn.commit()

def get_valid_reset_code(conn, email, code):
    """Return the reset row if the code is valid and not expired, else None."""
    row = conn.execute(
        'SELECT * FROM password_reset_codes WHERE email = ? AND code = ? AND datetime(expires_at) > datetime("now")',
        (email, code)
    ).fetchone()
    return row

def get_valid_reset_by_token(conn, token):
    """Return the reset row (with email) if the token is valid and not expired, else None."""
    if not token:
        return None
    row = conn.execute(
        'SELECT * FROM password_reset_codes WHERE code = ? AND datetime(expires_at) > datetime("now")',
        (token,)
    ).fetchone()
    return row

def invalidate_reset_code(conn, email):
    """Remove reset codes for this email (after successful reset)."""
    conn.execute('DELETE FROM password_reset_codes WHERE email = ?', (email,))
    conn.commit()

def update_user_password(conn, email, password_hash):
    """Update password for user with the given email."""
    conn.execute('UPDATE users SET password_hash = ? WHERE email = ?', (password_hash, email))
    conn.commit()
