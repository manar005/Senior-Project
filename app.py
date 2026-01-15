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
    
    # Insert network challenges if they don't exist
    cursor.execute('SELECT COUNT(*) FROM challenges WHERE order_num >= 11 AND order_num <= 20')
    network_challenges_count = cursor.fetchone()[0]
    if network_challenges_count == 0:
        network_challenges = [
            {
                'title': 'Wireshark Basics - HTTP Traffic',
                'description': 'You captured some network traffic. Analyze the HTTP packets to find the secret flag. The flag is hidden in an HTTP response header. Download the pcap file and use Wireshark to analyze it. Look for HTTP responses and check the headers.',
                'hint': 'Open the pcap file in Wireshark. Filter for HTTP traffic using "http" filter. Look at HTTP response packets and examine the headers. The flag might be in a custom header or in the response body.',
                'flag': 'NETWORK_HTTP_FLAG_2026',
                'expected_outcome': 'Learn to use Wireshark for packet analysis and understand HTTP protocol structure',
                'challenge_type': 'network',
                'challenge_data': 'Analyze HTTP packets in Wireshark. Filter: http. Check response headers.',
                'order_num': 11
            },
            {
                'title': 'TCP Handshake Analysis',
                'description': 'A suspicious connection was made. Analyze the TCP three-way handshake in the captured packets. What is the destination port number? Convert it to hexadecimal and that\'s your flag (format: PORT_0xXXXX).',
                'hint': 'In Wireshark, look for TCP SYN packets. The destination port is in the TCP header. Common ports: 80 (HTTP), 443 (HTTPS), 22 (SSH), 21 (FTP). Convert the decimal port to hex (e.g., 80 = 0x50).',
                'flag': 'PORT_0x1F90',
                'expected_outcome': 'Understand TCP handshake process and port identification',
                'challenge_type': 'network',
                'challenge_data': 'Find TCP SYN packet. Destination port is 8080 (0x1F90 in hex).',
                'order_num': 12
            },
            {
                'title': 'DNS Query Investigation',
                'description': 'Someone made a DNS query. What domain name was queried? The flag is the domain name in uppercase with underscores instead of dots (e.g., EXAMPLE_COM).',
                'hint': 'Filter for DNS packets in Wireshark using "dns" filter. Look at DNS query packets. The queried domain name is in the "Question" section. Convert dots to underscores and uppercase it.',
                'flag': 'SUSPICIOUS_DOMAIN_XYZ',
                'expected_outcome': 'Learn DNS protocol and how to analyze DNS queries',
                'challenge_type': 'network',
                'challenge_data': 'DNS query for suspicious.domain.xyz',
                'order_num': 13
            },
            {
                'title': 'ARP Spoofing Detection',
                'description': 'Detect ARP spoofing in this network capture. Find the MAC address that appears with multiple IP addresses (indicating ARP spoofing). The flag is that MAC address in uppercase with colons removed.',
                'hint': 'In Wireshark, filter for ARP packets using "arp" filter. Look for duplicate MAC addresses associated with different IP addresses. This indicates ARP spoofing. Extract the MAC address.',
                'flag': 'AA1122334455',
                'expected_outcome': 'Learn to detect ARP spoofing attacks through network analysis',
                'challenge_type': 'network',
                'challenge_data': 'MAC address AA:11:22:33:44:55 appears with multiple IPs',
                'order_num': 14
            },
            {
                'title': 'HTTPS/TLS Analysis',
                'description': 'Analyze this HTTPS connection. What TLS version was used? The flag format is TLS_VERSION_X_X (e.g., TLS_VERSION_1_3).',
                'hint': 'Filter for TLS/SSL packets using "tls" or "ssl" filter. Look at the Client Hello packet. The TLS version is shown in the handshake protocol. Common versions: 1.0, 1.1, 1.2, 1.3.',
                'flag': 'TLS_VERSION_1_2',
                'expected_outcome': 'Understand TLS/SSL handshake and version identification',
                'challenge_type': 'network',
                'challenge_data': 'TLS 1.2 handshake detected',
                'order_num': 15
            },
            {
                'title': 'ICMP Packet Analysis',
                'description': 'An ICMP packet was captured. What is the ICMP type code? The flag is ICMP_TYPE_X where X is the type code number.',
                'hint': 'Filter for ICMP packets using "icmp" filter. The ICMP type is in the ICMP header. Common types: 0 (Echo Reply), 8 (Echo Request), 3 (Destination Unreachable), 11 (Time Exceeded).',
                'flag': 'ICMP_TYPE_8',
                'expected_outcome': 'Learn ICMP protocol and packet types',
                'challenge_type': 'network',
                'challenge_data': 'ICMP Echo Request (Type 8) packet',
                'order_num': 16
            },
            {
                'title': 'FTP Credential Extraction',
                'description': 'An FTP connection was captured. Extract the username and password from the packets. The flag format is USERNAME_PASSWORD in uppercase.',
                'hint': 'Filter for FTP traffic using "ftp" filter. FTP sends credentials in plain text. Look for USER and PASS commands in the packet details. The username and password follow these commands.',
                'flag': 'ADMIN_SECRET123',
                'expected_outcome': 'Understand FTP protocol security issues and credential extraction',
                'challenge_type': 'network',
                'challenge_data': 'FTP login: admin / secret123',
                'order_num': 17
            },
            {
                'title': 'Port Scanning Detection',
                'description': 'A port scan was detected. What port range was scanned? The flag is SCAN_RANGE_X_Y where X is the first port and Y is the last port.',
                'hint': 'Look for multiple connection attempts to different ports from the same source IP. Filter by source IP and look at destination ports. Identify the range of ports that were scanned.',
                'flag': 'SCAN_RANGE_8080_8090',
                'expected_outcome': 'Learn to detect port scanning activities in network traffic',
                'challenge_type': 'network',
                'challenge_data': 'Ports 8080-8090 scanned from same source',
                'order_num': 18
            },
            {
                'title': 'Network Protocol Identification',
                'description': 'Identify the application layer protocol used in this communication. The flag is PROTOCOL_NAME in uppercase (e.g., SMTP, POP3, IMAP, SNMP).',
                'hint': 'Look at the application layer data in the packets. Check the port numbers and payload. Common protocols: SMTP (25), POP3 (110), IMAP (143), SNMP (161), Telnet (23).',
                'flag': 'SMTP',
                'expected_outcome': 'Learn to identify different network protocols from packet analysis',
                'challenge_type': 'network',
                'challenge_data': 'SMTP protocol on port 25',
                'order_num': 19
            },
            {
                'title': 'Network Forensics - Data Exfiltration',
                'description': 'Sensitive data was exfiltrated through DNS queries. Analyze the DNS packets and decode the base64-encoded data hidden in subdomain queries. The flag is the decoded message.',
                'hint': 'Filter for DNS queries. Look at the queried domain names. The data might be encoded in subdomains (e.g., dGhpc2lzYXRlc3Q=.example.com). Extract the base64 part before the domain and decode it.',
                'flag': 'NETWORK_EXFILTRATION_DETECTED',
                'expected_outcome': 'Learn advanced network forensics and DNS tunneling detection',
                'challenge_type': 'network',
                'challenge_data': 'Base64 in DNS: TkVUV09SS19FWElMVFJBVElPTl9ERVRFQ1RFRC5leGFtcGxlLmNvbQ==',
                'order_num': 20
            }
        ]
        
        for challenge in network_challenges:
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
    return render_template('home.html')

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
    
    conn.close()
    
    return render_template('dashboard.html', challenges=challenges, completed_ids=completed_ids, unlocked=unlocked, category='General Cybersecurity')

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
    
    conn.close()
    
    return render_template('dashboard.html', challenges=challenges, completed_ids=completed_ids, unlocked=unlocked, category='Network Security')

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
