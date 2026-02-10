from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
import secrets
from challenges import get_all_challenges, get_general_challenges, get_network_challenges

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

DATABASE = 'thaghrah.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_challenge_image():
    """Create a simple image for challenge 6 if it doesn't exist"""
    image_path = 'static/images/hidden_message.png'
    if not os.path.exists(image_path):
        os.makedirs('static/images', exist_ok=True)
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(img)
            text = "Thaghrah Challenge 6"
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            draw.text((50, 80), text, fill='black', font=font)
            draw.text((50, 120), "Check metadata or filename!", fill='gray', font=font)
            img.save(image_path)
        except ImportError:
            # If PIL is not available, create a placeholder
            with open(image_path, 'w') as f:
                f.write("Placeholder image. Flag: IMAGE_STEGANOGRAPHY_FLAG")

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add name column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN name TEXT')
    except sqlite3.OperationalError:
        # Column already exists, ignore
        pass
    
    # Challenges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            hint TEXT NOT NULL,
            flag TEXT NOT NULL,
            expected_outcome TEXT NOT NULL,
            challenge_type TEXT NOT NULL,
            challenge_data TEXT,
            order_num INTEGER NOT NULL
        )
    ''')
    
    # User progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (challenge_id) REFERENCES challenges(id),
            UNIQUE(user_id, challenge_id)
        )
    ''')
    
    # Badges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT NOT NULL,
            requirement_type TEXT NOT NULL,
            requirement_value INTEGER NOT NULL
        )
    ''')
    
    # User badges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_id INTEGER NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (badge_id) REFERENCES badges(id),
            UNIQUE(user_id, badge_id)
        )
    ''')
    
    # Insert badges if they don't exist
    cursor.execute('SELECT COUNT(*) FROM badges')
    if cursor.fetchone()[0] == 0:
        badges = [
            ('First Steps', 'Complete your first challenge', '🎯', 'challenges_completed', 1),
            ('Getting Started', 'Complete 3 challenges', '🌟', 'challenges_completed', 3),
            ('Halfway Hero', 'Complete 5 challenges', '🏆', 'challenges_completed', 5),
            ('Almost There', 'Complete 10 challenges', '💎', 'challenges_completed', 10),
            ('Champion', 'Complete 15 challenges', '👑', 'challenges_completed', 15),
            ('Master', 'Complete all 20 challenges', '🏅', 'challenges_completed', 20),
            ('General Expert', 'Complete all General Cybersecurity challenges', '🔐', 'category_completed', 10),
            ('Network Guru', 'Complete all Network Security challenges', '🌐', 'category_completed', 20),
            ('Quick Learner', 'Complete 3 challenges in one day', '⚡', 'daily_challenges', 3),
            ('Dedicated', 'Complete 5 challenges in one day', '🔥', 'daily_challenges', 5)
        ]
        cursor.executemany('''
            INSERT INTO badges (name, description, icon, requirement_type, requirement_value)
            VALUES (?, ?, ?, ?, ?)
        ''', badges)
    
    # Insert challenges if they don't exist
    cursor.execute('SELECT COUNT(*) FROM challenges')
    if cursor.fetchone()[0] == 0:
        challenges = get_all_challenges()
        
        for challenge in challenges:
            cursor.execute('''
                INSERT INTO challenges (title, description, hint, flag, expected_outcome, challenge_type, challenge_data, order_num)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                challenge['title'],
                challenge['description'],
                challenge['hint'],
                challenge['flag'],
                challenge['expected_outcome'],
                challenge['challenge_type'],
                challenge['challenge_data'],
                challenge['order_num']
            ))
    
    conn.commit()
    conn.close()

def check_and_award_badges(user_id, challenge_id):
    """Check if user qualifies for any badges and award them"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user's completed challenges
    completed = cursor.execute(
        'SELECT challenge_id FROM user_progress WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    completed_ids = [row[0] for row in completed]
    total_completed = len(completed_ids)
    
    # Get challenge info
    challenge = cursor.execute('SELECT * FROM challenges WHERE id = ?', (challenge_id,)).fetchone()
    
    # Get all badges
    badges = cursor.execute('SELECT * FROM badges').fetchall()
    
    # Get user's existing badges
    user_badges = cursor.execute(
        'SELECT badge_id FROM user_badges WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    user_badge_ids = [row[0] for row in user_badges]
    
    new_badges = []
    
    for badge in badges:
        if badge['id'] in user_badge_ids:
            continue  # User already has this badge
        
        requirement_type = badge['requirement_type']
        requirement_value = badge['requirement_value']
        
        if requirement_type == 'challenges_completed':
            if total_completed >= requirement_value:
                # Award badge
                cursor.execute(
                    'INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)',
                    (user_id, badge['id'])
                )
                new_badges.append(badge)
        
        elif requirement_type == 'category_completed':
            # Check if user completed all challenges in a category
            if requirement_value == 10:  # General challenges (1-10)
                general_challenges = cursor.execute(
                    'SELECT id FROM challenges WHERE order_num >= 1 AND order_num <= 10'
                ).fetchall()
                general_ids = [row[0] for row in general_challenges]
                if all(cid in completed_ids for cid in general_ids):
                    cursor.execute(
                        'INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)',
                        (user_id, badge['id'])
                    )
                    new_badges.append(badge)
            elif requirement_value == 20:  # Network challenges (11-20)
                network_challenges = cursor.execute(
                    'SELECT id FROM challenges WHERE order_num >= 11 AND order_num <= 20'
                ).fetchall()
                network_ids = [row[0] for row in network_challenges]
                if all(cid in completed_ids for cid in network_ids):
                    cursor.execute(
                        'INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)',
                        (user_id, badge['id'])
                    )
                    new_badges.append(badge)
    
    conn.commit()
    conn.close()
    return new_badges

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            return render_template('register.html', error='Name, email and password are required')
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            cursor.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', (name, email, password_hash))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            session['user_id'] = user_id
            session['email'] = email
            session['name'] = name
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error='Email already exists')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return render_template('login.html', error='Email and password are required')
        
        conn = get_db()
        cursor = conn.cursor()
        user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            if 'name' in user.keys() and user['name']:
                session['name'] = user['name']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user's badges
    user_badges = cursor.execute('''
        SELECT b.id, b.name, b.description, b.icon, ub.earned_at
        FROM badges b
        INNER JOIN user_badges ub ON b.id = ub.badge_id
        WHERE ub.user_id = ?
        ORDER BY ub.earned_at DESC
    ''', (session['user_id'],)).fetchall()
    
    # Get total badges count
    total_badges = cursor.execute('SELECT COUNT(*) FROM badges').fetchone()[0]
    
    conn.close()
    
    return render_template('home.html', user_badges=user_badges, total_badges=total_badges)

@app.route('/challenges/general')
@login_required
def general_challenges():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get general challenges (order_num 1-10)
    challenges = cursor.execute('SELECT * FROM challenges WHERE order_num >= 1 AND order_num <= 10 ORDER BY order_num').fetchall()
    
    # Get user's completed challenges
    completed = cursor.execute(
        'SELECT challenge_id FROM user_progress WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()
    completed_ids = [row[0] for row in completed]
    
    # Determine which challenges are unlocked (within this category)
    unlocked = []
    for i, challenge in enumerate(challenges):
        if i == 0 or challenges[i-1]['id'] in completed_ids:
            unlocked.append(challenge['id'])
    
    # Get user's badges
    user_badges = cursor.execute('''
        SELECT b.id, b.name, b.description, b.icon, ub.earned_at
        FROM badges b
        INNER JOIN user_badges ub ON b.id = ub.badge_id
        WHERE ub.user_id = ?
        ORDER BY ub.earned_at DESC
    ''', (session['user_id'],)).fetchall()
    
    total_badges = cursor.execute('SELECT COUNT(*) FROM badges').fetchone()[0]
    
    conn.close()
    
    return render_template('dashboard.html', challenges=challenges, completed_ids=completed_ids, unlocked=unlocked, category='General Cybersecurity', user_badges=user_badges, total_badges=total_badges)

@app.route('/challenges/network')
@login_required
def network_challenges():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get network challenges (order_num 11-20)
    challenges = cursor.execute('SELECT * FROM challenges WHERE order_num >= 11 AND order_num <= 20 ORDER BY order_num').fetchall()
    
    # Get user's completed challenges
    completed = cursor.execute(
        'SELECT challenge_id FROM user_progress WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()
    completed_ids = [row[0] for row in completed]
    
    # Determine which challenges are unlocked (within this category)
    unlocked = []
    for i, challenge in enumerate(challenges):
        if i == 0 or challenges[i-1]['id'] in completed_ids:
            unlocked.append(challenge['id'])
    
    # Get user's badges
    user_badges = cursor.execute('''
        SELECT b.id, b.name, b.description, b.icon, ub.earned_at
        FROM badges b
        INNER JOIN user_badges ub ON b.id = ub.badge_id
        WHERE ub.user_id = ?
        ORDER BY ub.earned_at DESC
    ''', (session['user_id'],)).fetchall()
    
    total_badges = cursor.execute('SELECT COUNT(*) FROM badges').fetchone()[0]
    
    conn.close()
    
    return render_template('dashboard.html', challenges=challenges, completed_ids=completed_ids, unlocked=unlocked, category='Network Security', user_badges=user_badges, total_badges=total_badges)

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all challenges
    challenges = cursor.execute('SELECT * FROM challenges ORDER BY order_num').fetchall()
    
    # Get user's completed challenges
    completed = cursor.execute(
        'SELECT challenge_id FROM user_progress WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()
    completed_ids = [row[0] for row in completed]
    
    # Determine which challenges are unlocked
    unlocked = []
    for i, challenge in enumerate(challenges):
        if i == 0 or challenges[i-1]['id'] in completed_ids:
            unlocked.append(challenge['id'])
    
    conn.close()
    
    return render_template('dashboard.html', challenges=challenges, completed_ids=completed_ids, unlocked=unlocked)

@app.route('/challenge/<int:challenge_id>')
@login_required
def challenge(challenge_id):
    from flask import make_response
    
    conn = get_db()
    cursor = conn.cursor()
    
    challenge = cursor.execute('SELECT * FROM challenges WHERE id = ?', (challenge_id,)).fetchone()
    
    if not challenge:
        conn.close()
        return redirect(url_for('home'))
    
    # Determine which category this challenge belongs to
    if challenge['order_num'] >= 1 and challenge['order_num'] <= 10:
        category = 'general'
        category_url = url_for('general_challenges')
    elif challenge['order_num'] >= 11 and challenge['order_num'] <= 20:
        category = 'network'
        category_url = url_for('network_challenges')
    else:
        category = 'general'
        category_url = url_for('general_challenges')
    
    # Get challenges from the same category for unlock checking
    if category == 'general':
        challenges = cursor.execute('SELECT * FROM challenges WHERE order_num >= 1 AND order_num <= 10 ORDER BY order_num').fetchall()
    else:
        challenges = cursor.execute('SELECT * FROM challenges WHERE order_num >= 11 AND order_num <= 20 ORDER BY order_num').fetchall()
    
    # Get user's completed challenges
    completed = cursor.execute(
        'SELECT challenge_id FROM user_progress WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()
    completed_ids = [row[0] for row in completed]
    
    # Check if challenge is unlocked (within its category)
    unlocked = []
    for i, ch in enumerate(challenges):
        if i == 0 or challenges[i-1]['id'] in completed_ids:
            unlocked.append(ch['id'])
    
    if challenge_id not in unlocked:
        conn.close()
        return redirect(category_url)
    
    # Check if already completed
    is_completed = challenge_id in completed_ids
    
    conn.close()
    
    # Set cookie for challenge 7 (Cookie Investigation)
    response = make_response(render_template('challenge.html', challenge=challenge, is_completed=is_completed, category_url=category_url))
    if challenge_id == 7:
        response.set_cookie('challenge_flag', 'COOKIE_FLAG_2024', max_age=3600)
    
    return response

@app.route('/submit_flag', methods=['POST'])
@login_required
def submit_flag():
    data = request.get_json()
    challenge_id = data.get('challenge_id')
    flag = data.get('flag')
    
    if not challenge_id or not flag:
        return jsonify({'success': False, 'message': 'Missing challenge ID or flag'})
    
    conn = get_db()
    cursor = conn.cursor()
    
    challenge = cursor.execute('SELECT * FROM challenges WHERE id = ?', (challenge_id,)).fetchone()
    
    if not challenge:
        conn.close()
        return jsonify({'success': False, 'message': 'Challenge not found'})
    
    # Check if flag is correct (case-insensitive)
    if flag.strip().upper() == challenge['flag'].upper():
        # Check if already completed
        existing = cursor.execute(
            'SELECT * FROM user_progress WHERE user_id = ? AND challenge_id = ?',
            (session['user_id'], challenge_id)
        ).fetchone()
        
        if not existing:
            cursor.execute(
                'INSERT INTO user_progress (user_id, challenge_id) VALUES (?, ?)',
                (session['user_id'], challenge_id)
            )
            conn.commit()
            
            # Check and award badges
            new_badges = check_and_award_badges(session['user_id'], challenge_id)
            badge_message = ''
            if new_badges:
                badge_names = [badge['name'] for badge in new_badges]
                badge_message = f' 🏆 Badge earned: {", ".join(badge_names)}!'
        
        conn.close()
        message = 'Correct! Challenge completed!' + badge_message if 'badge_message' in locals() else 'Correct! Challenge completed!'
        return jsonify({'success': True, 'message': message, 'new_badges': new_badges if 'new_badges' in locals() else []})
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Incorrect flag. Try again!'})

@app.route('/get_hint', methods=['POST'])
@login_required
def get_hint():
    data = request.get_json()
    challenge_id = data.get('challenge_id')
    
    if not challenge_id:
        return jsonify({'error': 'Missing challenge ID'})
    
    conn = get_db()
    cursor = conn.cursor()
    challenge = cursor.execute('SELECT hint FROM challenges WHERE id = ?', (challenge_id,)).fetchone()
    conn.close()
    
    if challenge:
        return jsonify({'hint': challenge['hint']})
    return jsonify({'error': 'Challenge not found'})

if __name__ == '__main__':
    init_db()
    create_challenge_image()
    app.run(debug=True, host='127.0.0.1', port=5001)
