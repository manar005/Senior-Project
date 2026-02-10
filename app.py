from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
import secrets
from challenges import get_network_challenges
import db_queries

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
    """Initialize database from schema.sql file"""
    conn = get_db()
    
    # Read and execute schema.sql file
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    conn.commit()
    
    # Insert badges if they don't exist
    if db_queries.get_badge_count(conn) == 0:
        badges_data = [
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
        conn.executemany('''
            INSERT INTO badges (name, description, icon, requirement_type, requirement_value)
            VALUES (?, ?, ?, ?, ?)
        ''', badges_data)
        conn.commit()
    
    # Insert challenges if they don't exist
    if db_queries.get_challenge_count(conn) == 0:
        challenges = get_network_challenges()
        
        # Prepare challenge data for batch insert
        challenge_data = []
        for idx, challenge in enumerate(challenges, start=1):
            challenge_data.append((
                challenge['title'],
                challenge['description'],
                challenge['hint'],
                challenge['flag'],
                challenge['expected_outcome'],
                challenge['challenge_type'],
                challenge['challenge_data'],
                idx
            ))
        
        # Use helper function for batch insert
        db_queries.insert_challenges(conn, challenge_data)
    
    conn.close()

def check_and_award_badges(user_id, challenge_id):
    """Check if user qualifies for any badges and award them"""
    conn = get_db()
    
    # Get user's completed challenges
    completed = db_queries.get_user_progress(conn, user_id)
    completed_ids = [row[0] for row in completed]
    total_completed = len(completed_ids)
    
    # Get all badges
    badges = db_queries.get_all_badges(conn)
    
    # Get user's existing badges
    user_badge_ids = db_queries.get_user_badge_ids(conn, user_id)
    
    new_badges = []
    
    for badge in badges:
        if badge['id'] in user_badge_ids:
            continue  # User already has this badge
        
        requirement_type = badge['requirement_type']
        requirement_value = badge['requirement_value']
        
        if requirement_type == 'challenges_completed':
            if total_completed >= requirement_value:
                # Award badge (function will check for duplicates)
                if db_queries.award_badge(conn, user_id, badge['id']):
                    new_badges.append(badge)
        
        elif requirement_type == 'category_completed':
            # Check if user completed all network challenges
            if requirement_value == 20:  # Network challenges
                challenges = db_queries.get_all_challenges(conn)
                challenge_ids = [ch['id'] for ch in challenges]
                if all(cid in completed_ids for cid in challenge_ids):
                    # Award badge (function will check for duplicates)
                    if db_queries.award_badge(conn, user_id, badge['id']):
                        new_badges.append(badge)
    
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
        confirm_password = request.form.get('confirm_password')
        
        if not name or not email or not password or not confirm_password:
            return render_template('register.html', error='All fields are required')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        conn = get_db()
        
        try:
            password_hash = generate_password_hash(password)
            user_id = db_queries.create_user(conn, name, email, password_hash)
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
        user = db_queries.get_user_by_email(conn, email)
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
    user_badges = db_queries.get_user_badges(conn, session['user_id'])
    total_badges = db_queries.get_total_badges_count(conn)
    conn.close()
    
    return render_template('home.html', user_badges=user_badges, total_badges=total_badges)


@app.route('/challenges/network')
@login_required
def network_challenges():
    conn = get_db()
    challenges = db_queries.get_all_challenges(conn)
    completed = db_queries.get_user_progress(conn, session['user_id'])
    completed_ids = [row[0] for row in completed]
    
    # Determine which challenges are unlocked
    unlocked = []
    for i, challenge in enumerate(challenges):
        if i == 0 or challenges[i-1]['id'] in completed_ids:
            unlocked.append(challenge['id'])
    
    user_badges = db_queries.get_user_badges(conn, session['user_id'])
    total_badges = db_queries.get_total_badges_count(conn)
    conn.close()
    
    return render_template('dashboard.html', challenges=challenges, completed_ids=completed_ids, unlocked=unlocked, category='Network Security', user_badges=user_badges, total_badges=total_badges)

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    challenges = db_queries.get_all_challenges(conn)
    completed = db_queries.get_user_progress(conn, session['user_id'])
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
    challenge = db_queries.get_challenge_by_id(conn, challenge_id)
    
    if not challenge:
        conn.close()
        return redirect(url_for('home'))
    
    # All challenges are network challenges now
    category_url = url_for('network_challenges')
    
    # Get all challenges for unlock checking
    challenges = db_queries.get_all_challenges(conn)
    completed = db_queries.get_user_progress(conn, session['user_id'])
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
    
    response = make_response(render_template('challenge.html', challenge=challenge, is_completed=is_completed, category_url=category_url))
    
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
    challenge = db_queries.get_challenge_by_id(conn, challenge_id)
    
    if not challenge:
        conn.close()
        return jsonify({'success': False, 'message': 'Challenge not found'})
    
    # Check if flag is correct (case-insensitive)
    if flag.strip().upper() == challenge['flag'].upper():
        # Check if already completed
        existing = db_queries.check_challenge_completed(conn, session['user_id'], challenge_id)
        
        if not existing:
            db_queries.complete_challenge(conn, session['user_id'], challenge_id)
            
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
    challenge = db_queries.get_challenge_by_id(conn, challenge_id)
    conn.close()
    
    if challenge:
        return jsonify({'hint': challenge['hint']})
    return jsonify({'error': 'Challenge not found'})

if __name__ == '__main__':
    init_db()
    create_challenge_image()
    app.run(debug=True, host='127.0.0.1', port=5001)
