from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
import secrets

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
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    
    # Insert challenges if they don't exist
    cursor.execute('SELECT COUNT(*) FROM challenges')
    if cursor.fetchone()[0] == 0:
        challenges = [
            {
                'title': 'Welcome to Thaghrah',
                'description': 'Your first challenge! Look at the page source. Sometimes the answer is hidden in plain sight.',
                'hint': 'Right-click and select "View Page Source" or press Ctrl+U',
                'flag': 'THAGHRAH_WELCOME_2024',
                'expected_outcome': 'Learn to inspect web page sources to find hidden information',
                'challenge_type': 'text',
                'challenge_data': '',
                'order_num': 1
            },
            {
                'title': 'Base64 Decoding',
                'description': 'You found this encoded message: VGhhZ2hyYWggQ2hhbGxlbmdlIDI=. Can you decode it?',
                'hint': 'Base64 is a common encoding scheme. Look for online decoders or Python libraries.',
                'flag': 'Thaghrah Challenge 2',
                'expected_outcome': 'Understand basic encoding/decoding techniques',
                'challenge_type': 'text',
                'challenge_data': 'VGhhZ2hyYWggQ2hhbGxlbmdlIDI=',
                'order_num': 2
            },
            {
                'title': 'ROT13 Cipher',
                'description': 'This message was encrypted with ROT13: Guntne Funyybj. Decode it to find the flag.',
                'hint': 'ROT13 shifts each letter by 13 positions. A becomes N, B becomes O, etc.',
                'flag': 'Thaghr Shyybow',
                'expected_outcome': 'Learn about Caesar cipher and substitution ciphers',
                'challenge_type': 'text',
                'challenge_data': 'Guntne Funyybj',
                'order_num': 3
            },
            {
                'title': 'Hexadecimal Decoding',
                'description': 'Decode this hexadecimal string: 54686167726168204368616C6C656E67652034',
                'hint': 'Convert each pair of hex digits to its ASCII character equivalent.',
                'flag': 'Thaghrah Challenge 4',
                'expected_outcome': 'Understand hexadecimal encoding and ASCII conversion',
                'challenge_type': 'text',
                'challenge_data': '54686167726168204368616C6C656E67652034',
                'order_num': 4
            },
            {
                'title': 'Morse Code',
                'description': 'Decode this Morse code: - .... .- --. .... .-. .- .... / -.-. .... .- .-.. .-.. . -. --. . / ....-',
                'hint': 'Morse code uses dots and dashes. Each letter has a unique pattern.',
                'flag': 'THAGHRAH CHALLENGE 5',
                'expected_outcome': 'Learn Morse code and pattern recognition',
                'challenge_type': 'text',
                'challenge_data': '- .... .- --. .... .-. .- .... / -.-. .... .- .-.. .-.. . -. --. . / ....-',
                'order_num': 5
            },
            {
                'title': 'Hidden in the Image',
                'description': 'There\'s a secret message hidden in this image. Can you find it?',
                'hint': 'Try using steganography tools or check the image metadata. Sometimes the answer is in the filename or EXIF data.',
                'flag': 'IMAGE_STEGANOGRAPHY_FLAG',
                'expected_outcome': 'Introduction to steganography and image analysis',
                'challenge_type': 'image',
                'challenge_data': 'hidden_message.png',
                'order_num': 6
            },
            {
                'title': 'Cookie Investigation',
                'description': 'Check your browser cookies. Sometimes important information is stored there.',
                'hint': 'Open browser developer tools (F12), go to Application/Storage tab, and check Cookies.',
                'flag': 'COOKIE_FLAG_2024',
                'expected_outcome': 'Learn about browser storage and cookies',
                'challenge_type': 'text',
                'challenge_data': '',
                'order_num': 7
            },
            {
                'title': 'URL Encoding',
                'description': 'Decode this URL-encoded string: %54%68%61%67%68%72%61%68%20%43%68%61%6C%6C%65%6E%67%65%20%38',
                'hint': 'URL encoding uses percent signs followed by hexadecimal values. Each %XX represents one character.',
                'flag': 'Thaghrah Challenge 8',
                'expected_outcome': 'Understand URL encoding and percent encoding',
                'challenge_type': 'text',
                'challenge_data': '%54%68%61%67%68%72%61%68%20%43%68%61%6C%6C%65%6E%67%65%20%38',
                'order_num': 8
            },
            {
                'title': 'Binary to Text',
                'description': 'Convert this binary string to text: 01010100 01101000 01100001 01100111 01101000 01110010 01100001 01101000 00100000 01000011 01101000 01100001 01101100 01101100 01100101 01101110 01100111 01100101 00100000 00111001',
                'hint': 'Each group of 8 bits represents one ASCII character. Convert each byte to decimal, then to its character.',
                'flag': 'Thaghrah Challenge 9',
                'expected_outcome': 'Learn binary representation and ASCII conversion',
                'challenge_type': 'text',
                'challenge_data': '01010100 01101000 01100001 01100111 01101000 01110010 01100001 01101000 00100000 01000011 01101000 01100001 01101100 01101100 01100101 01101110 01100111 01100101 00100000 00111001',
                'order_num': 9
            },
            {
                'title': 'Final Challenge - Combination',
                'description': 'You\'ve made it to the final challenge! This flag combines multiple techniques. The answer is: "THAGHRAH_FINAL_CHALLENGE_2024"',
                'hint': 'You\'ve learned many techniques. This is a straightforward final test. Just submit the flag!',
                'flag': 'THAGHRAH_FINAL_CHALLENGE_2024',
                'expected_outcome': 'Demonstrate mastery of basic cybersecurity concepts and encoding techniques',
                'challenge_type': 'text',
                'challenge_data': '',
                'order_num': 10
            }
        ]
        
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
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return render_template('register.html', error='Email and password are required')
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            session['user_id'] = user_id
            session['email'] = email
            return redirect(url_for('dashboard'))
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
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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
        return redirect(url_for('dashboard'))
    
    # Check if challenge is unlocked
    challenges = cursor.execute('SELECT * FROM challenges ORDER BY order_num').fetchall()
    completed = cursor.execute(
        'SELECT challenge_id FROM user_progress WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()
    completed_ids = [row[0] for row in completed]
    
    unlocked = []
    for i, ch in enumerate(challenges):
        if i == 0 or challenges[i-1]['id'] in completed_ids:
            unlocked.append(ch['id'])
    
    if challenge_id not in unlocked:
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Check if already completed
    is_completed = challenge_id in completed_ids
    
    conn.close()
    
    # Set cookie for challenge 7 (Cookie Investigation)
    response = make_response(render_template('challenge.html', challenge=challenge, is_completed=is_completed))
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
        
        conn.close()
        return jsonify({'success': True, 'message': 'Correct! Challenge completed!'})
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
    app.run(debug=True)
