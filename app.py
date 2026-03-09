from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
import secrets
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from challenges import get_network_challenges
import db_queries

# Protocol/category names (8 categories; TCP has 3 challenges under it)
PROTOCOL_NAMES = [
    'HTTP', 'TCP', 'DNS', 'FTP', 'ICMP', 'SMTP', 'TLS', 'Forensics'
]
# Map challenge category_slug to category order_num (1-based)
CATEGORY_SLUG_TO_ORDER = {
    'http': 1, 'tcp': 2, 'dns': 3, 'ftp': 4,
    'icmp': 5, 'smtp': 6, 'tls': 7, 'forensics': 8,
}

PROTOCOL_DETAILS = {
    'HTTP': {
        'overview': 'HTTP powers web browsing by carrying requests and responses between clients and servers.',
        'common_ports': '80, 8080',
        'focus': 'Methods, headers, status codes, cookies, and suspicious web requests.',
        'why_it_matters': 'Understanding HTTP helps you investigate websites, APIs, and common web attacks.'
    },
    'TCP': {
        'overview': 'TCP is a reliable transport protocol that manages connection setup, ordering, retransmission, and flow control.',
        'common_ports': 'Used by many apps, including 80, 443, 22, and 25',
        'focus': 'Three-way handshake, sequence numbers, retransmissions, resets, and fragmentation behavior.',
        'why_it_matters': 'TCP analysis is essential for debugging connectivity issues and spotting transport-layer anomalies.'
    },
    'DNS': {
        'overview': 'DNS translates domain names into IP addresses so users can reach services by name instead of numbers.',
        'common_ports': '53 UDP and 53 TCP',
        'focus': 'Queries, answers, record types, response codes, and unusual domain lookups.',
        'why_it_matters': 'DNS traffic often reveals command-and-control activity, data exfiltration, or simple misconfigurations.'
    },
    'FTP': {
        'overview': 'FTP transfers files between hosts using separate control and data connections.',
        'common_ports': '21 control, 20 data',
        'focus': 'Login attempts, file transfers, directory listings, and credentials sent in clear text.',
        'why_it_matters': 'FTP is insecure by default, so it is useful for learning how exposed credentials and file activity appear on the wire.'
    },
    'ICMP': {
        'overview': 'ICMP is used for network diagnostics and control messages such as echo requests and unreachable notifications.',
        'common_ports': 'No ports - ICMP uses message types and codes',
        'focus': 'Echo request/reply, TTL behavior, unreachable errors, and latency troubleshooting.',
        'why_it_matters': 'ICMP helps you understand path visibility, host reachability, and reconnaissance behavior.'
    },
    'SMTP': {
        'overview': 'SMTP is the protocol used to send email between clients and mail servers.',
        'common_ports': '25, 465, 587',
        'focus': 'Mail commands, sender and recipient flow, headers, and attachment delivery patterns.',
        'why_it_matters': 'SMTP analysis is valuable for investigating phishing, spoofing, and suspicious outbound mail traffic.'
    },
    'TLS': {
        'overview': 'TLS protects application traffic by encrypting communication between endpoints.',
        'common_ports': 'Usually carried over TCP 443',
        'focus': 'Handshake steps, certificates, SNI, versions, cipher suites, and trust validation.',
        'why_it_matters': 'TLS inspection teaches you how secure sessions are established and where weak configurations appear.'
    },
    'Forensics': {
        'overview': 'Forensics challenges focus on extracting evidence, reconstructing events, and identifying hidden indicators from captures or files.',
        'common_ports': 'Varies by artifact and investigation scope',
        'focus': 'Timeline reconstruction, embedded clues, unusual files, and evidence correlation.',
        'why_it_matters': 'Forensics skills help you move from raw data to a clear explanation of what happened and why.'
    }
}

import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

DATABASE = 'thaghrah.db'

def validate_password(password):
    """Validate password: at least 8 chars, one uppercase letter, one special character."""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long.'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one capital letter.'
    if not re.search(r'[^A-Za-z0-9]', password):
        return False, 'Password must contain at least one special character.'
    return True, None


def get_protocol_details(protocol_name):
    return PROTOCOL_DETAILS.get(protocol_name, {
        'overview': 'Explore this protocol through hands-on packet analysis challenges.',
        'common_ports': 'Varies by implementation',
        'focus': 'Traffic structure, message flow, and observable indicators.',
        'why_it_matters': 'Learning this protocol improves your network analysis and incident response skills.'
    })


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def send_reset_link_email(to_email, reset_link):
    """Send password reset link. Uses SMTP from env or prints to console."""
    subject = 'Thaghrah – Reset your password'
    body = f'''Hello,\n\nYou requested a password reset for your Thaghrah account.\n\nClick the link below to set a new password (link expires in 15 minutes):\n\n{reset_link}\n\nIf you did not request this, please ignore this email.\n\n— Thaghrah\n'''
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = os.environ.get('MAIL_FROM', 'noreply@thaghrah.local')
    msg['To'] = to_email
    msg.attach(MIMEText(body, 'plain'))
    server = os.environ.get('MAIL_SERVER')
    if not server:
        print(f'[MAIL] No MAIL_SERVER set. Password reset link for {to_email}:\n{reset_link}')
        return True
    try:
        port = int(os.environ.get('MAIL_PORT', '587'))
        use_tls = os.environ.get('MAIL_USE_TLS', '1').lower() in ('1', 'true', 'yes')
        username = os.environ.get('MAIL_USERNAME')
        password = os.environ.get('MAIL_PASSWORD')
        with smtplib.SMTP(server, port) as smtp:
            if use_tls:
                smtp.starttls()
            if username and password:
                smtp.login(username, password)
            smtp.sendmail(msg['From'], [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f'[MAIL] Failed to send reset email: {e}')
        return False


def init_db():
    """Initialize database from schema.sql file"""
    conn = get_db()
    
    # Read and execute schema.sql file
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    
    # Migration: add points/used_hint/points_earned to existing databases
    for sql in [
        'ALTER TABLE challenges ADD COLUMN points INTEGER NOT NULL DEFAULT 100',
        'ALTER TABLE user_progress ADD COLUMN used_hint INTEGER NOT NULL DEFAULT 0',
        'ALTER TABLE user_progress ADD COLUMN points_earned INTEGER NOT NULL DEFAULT 0',
    ]:
        try:
            conn.execute(sql)
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists

    # Migration: password_reset_codes table for forgot-password flow
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                code TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Migration: challenge_categories and category_id on challenges
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS challenge_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                order_num INTEGER NOT NULL
            )
        ''')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE challenges ADD COLUMN category_id INTEGER')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    if db_queries.get_category_count(conn) == 0:
        category_data = [(PROTOCOL_NAMES[idx], idx + 1) for idx in range(len(PROTOCOL_NAMES))]
        db_queries.insert_categories(conn, category_data)
        conn.commit()
    else:
        # Only overwrite category titles when we have exactly 8 categories (new structure).
        # If we have 10 categories (TCP, TCP Handshake Count, TCP Fragmentation, etc.), leave
        # them so the view can merge TCP subcategories and show 3 TCP challenges.
        if db_queries.get_category_count(conn) == 8:
            for idx, name in enumerate(PROTOCOL_NAMES, start=1):
                try:
                    conn.execute('UPDATE challenge_categories SET title = ? WHERE order_num = ?', (name, idx))
                    conn.commit()
                except sqlite3.OperationalError:
                    pass
        # Migration: move challenges from "TCP Handshake Count" and "TCP Fragmentation" into "TCP"
        # so all 3 TCP challenges appear under one category (works for both 8 and 10 category DBs).
        try:
            categories = db_queries.get_all_categories(conn)
            tcp_primary = next((c for c in categories if c['title'] == 'TCP'), None)
            tcp_extra = [c for c in categories if c['title'] in ('TCP Handshake Count', 'TCP Fragmentation')]
            if tcp_primary and tcp_extra:
                tcp_id = tcp_primary['id']
                extra_ids = [c['id'] for c in tcp_extra]
                # Assign order_num 2 and 3 within TCP for the moved challenges (keep existing TCP challenge as 1)
                cur = conn.execute(
                    'SELECT id, order_num FROM challenges WHERE category_id IN ({}) ORDER BY category_id, order_num'.format(
                        ','.join('?' * len(extra_ids))
                    ),
                    extra_ids
                )
                rows = cur.fetchall()
                for i, row in enumerate(rows):
                    conn.execute(
                        'UPDATE challenges SET category_id = ?, order_num = ? WHERE id = ?',
                        (tcp_id, i + 2, row['id'])  # order_num 2, 3 within TCP
                    )
                conn.commit()
                # Remove the now-empty TCP subcategory rows so we have 8 categories
                for cid in extra_ids:
                    conn.execute('DELETE FROM challenge_categories WHERE id = ?', (cid,))
                conn.commit()
                # Renumber so remaining categories have order_num 1-8 (e.g. 9->7, 10->8)
                conn.execute('UPDATE challenge_categories SET order_num = 7 WHERE order_num = 9')
                conn.execute('UPDATE challenge_categories SET order_num = 8 WHERE order_num = 10')
                conn.commit()
                # Re-point TLS and Forensics challenges: they had category_id 7 and 8 (now deleted).
                # After delete, TLS and Forensics have ids 9 and 10; fix challenges 9 and 10 to point to them.
                conn.execute('UPDATE challenges SET category_id = 9 WHERE id = 9')
                conn.execute('UPDATE challenges SET category_id = 10 WHERE id = 10')
                conn.commit()
            elif tcp_primary:
                # Fallback: if titles were already overwritten, ensure challenge ids 2, 7, 8 are under TCP
                tcp_id = tcp_primary['id']
                for challenge_id, order_in_tcp in [(2, 1), (7, 2), (8, 3)]:
                    conn.execute(
                        'UPDATE challenges SET category_id = ?, order_num = ? WHERE id = ?',
                        (tcp_id, order_in_tcp, challenge_id)
                    )
                conn.commit()
        except (sqlite3.OperationalError, StopIteration):
            pass
        # Ensure Forensics challenge (id 10) points to the right category (fix orphaned refs)
        try:
            categories = db_queries.get_all_categories(conn)
            forensics_cat = next((c for c in categories if c['title'] == 'Forensics'), None)
            if forensics_cat:
                conn.execute('UPDATE challenges SET category_id = ? WHERE id = 10', (forensics_cat['id'],))
            conn.commit()
        except (sqlite3.OperationalError, StopIteration):
            pass
    try:
        conn.execute('''
            UPDATE challenges SET category_id = (
                SELECT id FROM challenge_categories WHERE challenge_categories.order_num = challenges.order_num
            ) WHERE category_id IS NULL
        ''')
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Insert badges if they don't exist
    if db_queries.get_badge_count(conn) == 0:
        badges_data = [
            ('First Steps', 'Complete your first network challenge', '🎯', 'challenges_completed', 1),
            ('Getting Started', 'Complete 3 network challenges', '🌟', 'challenges_completed', 3),
            ('Halfway Hero', 'Complete 5 network challenges', '🏆', 'challenges_completed', 5),
            ('Network Expert', 'Complete 7 network challenges', '💎', 'challenges_completed', 7),
            ('Network Master', 'Complete all 10 network challenges', '🏅', 'challenges_completed', 10),
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
        network_challenges = get_network_challenges()
        categories = db_queries.get_all_categories(conn)
        by_order = {c['order_num']: c['id'] for c in categories}
        challenge_data = []
        for c in network_challenges:
            cat_order = CATEGORY_SLUG_TO_ORDER.get(c.get('category_slug'), 1)
            category_id = by_order.get(cat_order, list(by_order.values())[0])
            order_in_cat = c.get('order_in_category', 1)
            challenge_data.append((
                category_id, c['title'], c['description'], c['hint'], c['flag'],
                c['expected_outcome'], c['challenge_type'], c.get('challenge_data'),
                order_in_cat, c.get('points', 100)
            ))
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
        
        elif requirement_type == 'daily_challenges':
            # Check if user completed required number of challenges today
            from datetime import date
            today = date.today().isoformat()
            daily_completed = conn.execute(
                'SELECT COUNT(DISTINCT challenge_id) FROM user_progress WHERE user_id = ? AND DATE(completed_at) = ?',
                (user_id, today)
            ).fetchone()[0]
            # Award badge (function will check for duplicates)
            if daily_completed >= requirement_value and db_queries.award_badge(conn, user_id, badge['id']):
                new_badges.append(badge)

    conn.close()
    return new_badges

def get_unlocked_challenges(challenges, completed_ids):
    """Helper function to determine which challenges are unlocked"""
    unlocked = []
    for i, challenge in enumerate(challenges):
        if i == 0 or challenges[i-1]['id'] in completed_ids:
            unlocked.append(challenge['id'])
    return unlocked

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
    return render_template('start.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not name or not email or not password or not confirm_password:
            return render_template('register.html', error='All fields are required')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        conn = get_db()
        existing = db_queries.get_user_by_email(conn, email)
        if existing:
            conn.close()
            return render_template('register.html', error='This email is already registered. Please sign in or use a different email.')
        
        valid, msg = validate_password(password)
        if not valid:
            conn.close()
            return render_template('register.html', error=msg)
        
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
            return render_template('register.html', error='This email is already registered. Please sign in or use a different email.')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
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
    
    success = request.args.get('reset') == '1'
    return render_template('login.html', success=success)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        if not email:
            return render_template('forgot_password.html', error='Please enter your email')
        conn = get_db()
        user = db_queries.get_user_by_email(conn, email)
        conn.close()
        if not user:
            return render_template('forgot_password.html', error='No account found with that email')
        token = secrets.token_urlsafe(32)
        expires_at = (datetime.utcnow() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db()
        db_queries.create_reset_code(conn, email, token, expires_at)
        conn.close()
        reset_link = url_for('reset_password', token=token, _external=True)
        send_reset_link_email(email, reset_link)
        demo_link = reset_link if not os.environ.get('MAIL_SERVER') else None
        return render_template('forgot_password.html', success=True, email=email, demo_link=demo_link)
    return render_template('forgot_password.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    # If user arrived via the email link (token in URL), validate and store in session then redirect to clean URL
    if token:
        conn = get_db()
        row = db_queries.get_valid_reset_by_token(conn, token)
        conn.close()
        if row:
            session['reset_email'] = row['email']
            session['reset_token'] = token
            return redirect(url_for('reset_password'))
        return render_template('reset_password.html', error='This link is invalid or has expired. Please request a new one.')
    reset_email = session.get('reset_email')
    reset_token = session.get('reset_token')
    if not reset_email or not reset_token:
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        new_password = request.form.get('new_password') or ''
        confirm_password = request.form.get('confirm_password') or ''
        if not new_password or not confirm_password:
            return render_template('reset_password.html', reset_email=reset_email, error='Both password fields are required')
        if new_password != confirm_password:
            return render_template('reset_password.html', reset_email=reset_email, error='Passwords do not match')
        valid, msg = validate_password(new_password)
        if not valid:
            return render_template('reset_password.html', reset_email=reset_email, error=msg)
        conn = get_db()
        row = db_queries.get_valid_reset_by_token(conn, reset_token)
        if not row or row['email'] != reset_email:
            conn.close()
            session.pop('reset_email', None)
            session.pop('reset_token', None)
            return render_template('reset_password.html', error='This link has expired. Please request a new one from Forgot password.')
        db_queries.invalidate_reset_code(conn, reset_email)
        password_hash = generate_password_hash(new_password)
        db_queries.update_user_password(conn, reset_email, password_hash)
        conn.close()
        session.pop('reset_email', None)
        session.pop('reset_token', None)
        return redirect(url_for('login') + '?reset=1')
    return render_template('reset_password.html', reset_email=reset_email)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/me')
@login_required
def api_me():
    """Return current user stats for nav (points, badges)."""
    conn = get_db()
    total_points = db_queries.get_user_total_points(conn, session['user_id'])
    badges = db_queries.get_user_badges(conn, session['user_id'])
    conn.close()
    return jsonify({'points': total_points, 'badges': len(badges)})

@app.route('/home')
@login_required
def home():
    conn = get_db()
    user_badges = db_queries.get_user_badges(conn, session['user_id'])
    total_badges = db_queries.get_total_badges_count(conn)
    total_points = db_queries.get_user_total_points(conn, session['user_id'])
    conn.close()
    
    return render_template('home.html', user_badges=user_badges, total_badges=total_badges, total_points=total_points)

@app.route('/challenges/network')
@login_required
def network_challenges():
    conn = get_db()
    categories = db_queries.get_all_categories(conn)
    all_challenges = db_queries.get_all_challenges_ordered(conn)
    completed = db_queries.get_user_progress(conn, session['user_id'])
    completed_ids = [row[0] for row in completed]
    unlocked = get_unlocked_challenges(all_challenges, completed_ids)
    # Build exactly 8 protocol cards (merge TCP subcategories for display)
    categories_with_challenges = []
    for protocol_name in PROTOCOL_NAMES:
        # Primary category: the one whose title exactly matches (e.g. "TCP", "HTTP")
        primary = next((c for c in categories if c['title'] == protocol_name), None)
        if not primary:
            continue
        # For TCP, include challenges from "TCP", "TCP Handshake Count", "TCP Fragmentation"
        if protocol_name == 'TCP':
            tcp_cat_ids = [c['id'] for c in categories if c['title'] == 'TCP' or c['title'].startswith('TCP ')]
            challenges_in_cat = db_queries.get_challenges_by_category_ids(conn, tcp_cat_ids)
        else:
            challenges_in_cat = db_queries.get_challenges_by_category(conn, primary['id'])
        categories_with_challenges.append({'category': primary, 'challenges': challenges_in_cat})
    user_badges = db_queries.get_user_badges(conn, session['user_id'])
    total_badges = db_queries.get_total_badges_count(conn)
    total_points = db_queries.get_user_total_points(conn, session['user_id'])
    conn.close()
    return render_template(
        'dashboard.html',
        categories_with_challenges=categories_with_challenges,
        all_challenges=all_challenges,
        completed_ids=completed_ids,
        unlocked=unlocked,
        category='Network Security',
        user_badges=user_badges,
        total_badges=total_badges,
        total_points=total_points
    )


@app.route('/challenges/network/category/<int:category_id>')
@login_required
def category_challenges(category_id):
    """Show challenges for one protocol/category. TCP merges all TCP subcategories."""
    conn = get_db()
    cat = db_queries.get_category_by_id(conn, category_id)
    if not cat:
        conn.close()
        return redirect(url_for('network_challenges'))
    all_challenges = db_queries.get_all_challenges_ordered(conn)
    completed = db_queries.get_user_progress(conn, session['user_id'])
    completed_ids = [row[0] for row in completed]
    unlocked = get_unlocked_challenges(all_challenges, completed_ids)
    if cat['title'] == 'TCP':
        categories = db_queries.get_all_categories(conn)
        tcp_cat_ids = [c['id'] for c in categories if c['title'] == 'TCP' or c['title'].startswith('TCP ')]
        challenges = db_queries.get_challenges_by_category_ids(conn, tcp_cat_ids)
    else:
        challenges = db_queries.get_challenges_by_category(conn, category_id)
    user_badges = db_queries.get_user_badges(conn, session['user_id'])
    total_badges = db_queries.get_total_badges_count(conn)
    total_points = db_queries.get_user_total_points(conn, session['user_id'])
    conn.close()
    completed_in_category = sum(1 for c in challenges if c['id'] in completed_ids)
    return render_template(
        'category_challenges.html',
        category=cat,
        protocol_details=get_protocol_details(cat['title']),
        challenges=challenges,
        completed_ids=completed_ids,
        completed_in_category=completed_in_category,
        unlocked=unlocked,
        all_challenges=all_challenges,
        user_badges=user_badges,
        total_badges=total_badges,
        total_points=total_points
    )


@app.route('/challenge/<int:challenge_id>')
@login_required
def challenge(challenge_id):
    if challenge_id < 1:
        return redirect(url_for('network_challenges'))
    conn = get_db()
    challenge = db_queries.get_challenge_by_id(conn, challenge_id)
    if not challenge:
        conn.close()
        return redirect(url_for('network_challenges'))
    challenges = db_queries.get_all_challenges(conn)
    completed = db_queries.get_user_progress(conn, session['user_id'])
    completed_ids = [row[0] for row in completed]
    unlocked = get_unlocked_challenges(challenges, completed_ids)
    if challenge_id not in unlocked:
        conn.close()
        return redirect(url_for('network_challenges'))
    conn.close()
    return render_template(
        'challenge.html',
        challenge=challenge,
        is_completed=challenge_id in completed_ids,
        category_url=url_for('category_challenges', category_id=challenge['category_id'])
    )

@app.route('/submit_flag', methods=['POST'])
@login_required
def submit_flag():
    data = request.get_json(silent=True) or {}
    challenge_id = data.get('challenge_id')
    flag = data.get('flag')
    used_hint = bool(data.get('used_hint', False))
    
    if challenge_id is None or flag is None:
        return jsonify({'success': False, 'message': 'Missing challenge ID or flag'})
    # Coerce flag to string and strip (in case of number or extra whitespace)
    flag = str(flag).strip()
    if not flag:
        return jsonify({'success': False, 'message': 'Please enter a flag'})
    try:
        challenge_id = int(challenge_id)
        if challenge_id < 1:
            return jsonify({'success': False, 'message': 'Invalid challenge ID'})
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid challenge ID'})
    
    conn = get_db()
    challenge = db_queries.get_challenge_by_id(conn, challenge_id)
    
    if not challenge:
        conn.close()
        return jsonify({'success': False, 'message': 'Challenge not found'})
    # Normalize: strip whitespace, handle bytes/str from DB, remove invisible chars
    def normalize_flag(s):
        if s is None:
            return ''
        if isinstance(s, bytes):
            s = s.decode('utf-8', errors='ignore')
        s = str(s).strip().replace('\r', '').replace('\n', '')
        for c in '\ufeff\u200b\u200c\u200d\u200e\u200f':
            s = s.replace(c, '')
        return s.upper()
    stored_flag = challenge['flag']
    if stored_flag is None:
        stored_flag = ''
    if normalize_flag(flag) == normalize_flag(stored_flag):
        existing = db_queries.check_challenge_completed(conn, session['user_id'], challenge_id)
        new_badges = []
        badge_message = ''
        points_earned = 0
        base_points = 100
        if 'points' in challenge.keys():
            try:
                base_points = int(challenge['points'])
            except (TypeError, ValueError):
                pass
        if used_hint:
            points_earned = max(0, base_points // 2)  # 50% when hint used
        else:
            points_earned = base_points
        if not existing:
            db_queries.complete_challenge(conn, session['user_id'], challenge_id, used_hint=used_hint, points_earned=points_earned)
            new_badges = check_and_award_badges(session['user_id'], challenge_id)
            if new_badges:
                badge_names = [badge['name'] for badge in new_badges]
                badge_message = f' 🏆 Badge earned: {", ".join(badge_names)}!'
        
        conn.close()
        message = f'Correct! Challenge completed! +{points_earned} points.' + badge_message
        return jsonify({'success': True, 'message': message, 'new_badges': new_badges, 'points_earned': points_earned})
    conn.close()
    return jsonify({'success': False, 'message': 'Incorrect flag. Try again!'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5001)
