# Thaghrah — Audit Explanation

# Part 1: Project Logic

## 1.1 Purpose

**Thaghrah** is an educational, web-based cybersecurity learning platform for first-year students. It is a **game-like** environment where users:

1. Create an account and log in.
2. Work through **10 network security challenges** in order.
3. Analyze **pcap** (packet capture) files in **Wireshark** to find a **flag** for each challenge.
4. Submit the flag in the app to complete the challenge and unlock the next one.
5. Earn **points** for each correct flag (full points without hint, half points if the hint was used).
6. Earn **badges** for milestones (e.g. first challenge, 3 challenges, 5 in one day).

Core loop: **Register → Login → Open challenge → Download pcap → Analyze in Wireshark → Submit flag → Earn points (and possibly a badge) → Unlock next challenge.**

## 1.2 High-Level Flow

```
User visits app
    → Not logged in: redirect to Login (or Register)
    → Logged in: redirect to Home

Home
    → Shows welcome, points & badges summary, link to "Network Security" challenges

Network Challenges (/challenges/network)
    → Lists 10 challenges with status: Locked / Start / Completed
    → Only Challenge 1 is unlocked initially
    → Unlock rule: complete challenge N to unlock challenge N+1

Challenge page (e.g. /challenge/1)
    → Shows: Expected Outcome, Description, (optional) Download pcap, Hint, Submit Flag
    → User may click "Show hint" (reduces points for that challenge)
    → User downloads pcap, uses Wireshark, finds flag, types it in, submits

Submit flag (POST /submit_flag)
    → Expects JSON: challenge_id, flag, used_hint (boolean)
    → Server compares submitted flag to stored flag (case-insensitive, normalized)
    → If correct: record completion in user_progress with used_hint and points_earned;
                  check badges; return success, message (incl. +X points), new_badges
    → If wrong: return "Incorrect flag. Try again!"

Points
    → Each challenge has a base points value (e.g. 100). Full points if user did not use hint;
      half points if they used the hint before solving. points_earned stored per completion.

Badges
    → Awarded when user meets criteria (e.g. 1, 3, 5, 7, 10 challenges completed; or 3/5 challenges in one day)
    → Stored in user_badges; shown on Home and Dashboard
```

## 1.3 Data Model (Logic)

- **Users**: One row per account (id, name, email, password_hash). Passwords hashed with Werkzeug; never stored in plain text.
- **Challenges**: 10 rows, one per challenge (title, description, hint, flag, expected_outcome, challenge_type, challenge_data, order_num, **points**). Content is loaded from Python files in `challenges/` on first run and inserted into the DB.
- **User progress**: One row per (user, challenge) when a user completes a challenge. Columns: user_id, challenge_id, completed_at, **used_hint**, **points_earned**. Used to show “Completed”, compute unlock (complete N → unlock N+1), and compute total points.
- **Badges**: Fixed set of badge definitions (name, description, icon, requirement_type, requirement_value).
- **User badges**: One row per (user, badge) when a user earns a badge. Shown as “Your Badges” on Home and Dashboard.

## 1.4 Security-Related Logic

- **Authentication**: Login sets `session['user_id']` (and email, name). Protected routes use `@login_required`; redirect to login if `user_id` not in session.
- **Flag verification**: Server-side only. Stored flag in DB; comparison is normalized (strip, upper, remove invisible chars). No client-side flag validation.
- **Challenge access**: A user can open a challenge only if its ID is in the **unlocked** list (Challenge 1 always unlocked; others unlock after completing the previous one). Direct URL access to a locked challenge redirects to the challenges list.
- **Passwords**: Stored as hashes (Werkzeug); never logged or sent to the client except during login (password sent over HTTPS in production).

---

# Part 2: Code in Detail

## 2.1 Technology Stack

- **Backend**: Flask (Python).
- **Frontend**: HTML templates (Jinja2), CSS, vanilla JavaScript. Fonts: Outfit, JetBrains Mono (Google Fonts).
- **Database**: SQLite (`thaghrah.db`), created and migrated via `schema.sql`.
- **Auth**: Werkzeug `generate_password_hash` / `check_password_hash`; session-based (server-side session, secret key).

## 2.2 Entry Point and Database Setup

**File: `app.py`**

- **`if __name__ == '__main__'`**: Calls `init_db()` then `app.run(debug=True, host='127.0.0.1', port=5001)`.
- **`init_db()`**:
  1. Opens a connection and runs **`schema.sql`** (creates tables if not exist).
  2. **Migration**: For existing DBs, runs ALTER TABLE to add `challenges.points`, `user_progress.used_hint`, `user_progress.points_earned` if missing (ignores errors if columns already exist).
  3. If no badges exist: inserts the 7 predefined badges (e.g. “First Steps”, “Getting Started”, …).
  4. If no challenges exist: calls **`get_network_challenges()`** from the `challenges` package, builds rows (title, description, hint, flag, expected_outcome, challenge_type, challenge_data, order_num, **points**), and calls **`db_queries.insert_challenges(conn, challenge_data)`** to insert all 10 challenges.

Source of truth for challenge text and flags is the Python files in `challenges/`; the DB is populated once at first run. Later edits to those files do not auto-update the DB; the app reads from the DB.

- **`get_db()`**: Returns a SQLite connection with **`row_factory = sqlite3.Row`** so results behave like dicts (e.g. `row['email']`).

## 2.3 Database Layer

**File: `schema.sql`**

- **users**: id, name, email (UNIQUE), password_hash, created_at.
- **challenges**: id, title, description, hint, flag, expected_outcome, challenge_type, challenge_data, order_num, **points** (INTEGER NOT NULL DEFAULT 100).
- **user_progress**: id, user_id, challenge_id, completed_at, **used_hint** (INTEGER NOT NULL DEFAULT 0), **points_earned** (INTEGER NOT NULL DEFAULT 0); UNIQUE(user_id, challenge_id); foreign keys to users and challenges.
- **badges**: id, name, description, icon, requirement_type, requirement_value.
- **user_badges**: id, user_id, badge_id, earned_at; UNIQUE(user_id, badge_id); foreign keys.

**File: `db_queries.py`**

- All functions take a **connection `conn`** (and relevant IDs/values). Caller opens/closes the connection.
- **User**: `get_user_by_email`, `create_user`.
- **Challenges**: `get_all_challenges`, `get_challenge_by_id`, `get_challenge_count`, `insert_challenges` (includes **points** column).
- **Progress**: `get_user_progress` (returns rows with challenge_id, points_earned, used_hint), `check_challenge_completed`, **`complete_challenge(conn, user_id, challenge_id, used_hint=False, points_earned=0)`** (inserts into user_progress if not already completed; returns True/False), **`get_user_total_points(conn, user_id)`** (SUM of points_earned).
- **Badges**: `get_all_badges`, `get_badge_count`, `get_user_badges`, `get_user_badge_ids`, `get_total_badges_count`, `award_badge`.

SQL and DB access are centralized here for easier auditing and testing.

## 2.4 Challenges Module

**File: `challenges/__init__.py`**

- Imports `challenge_01` … `challenge_10` (each defines a dict `challenge`).
- **`get_network_challenges()`** returns `[challenge_01, challenge_02, …]` in order 1–10.

**Files: `challenges/challenge_01.py` … `challenge_10.py`**

- Each defines **`challenge`** with: title, description, hint, flag, expected_outcome, challenge_type, order_num, **points** (default 100), and optionally challenge_data. The **flag** is the string the user must submit. The app uses the database at runtime for display and validation; the Python files are used only for seeding (and any sync tooling).

**Current 10 challenges (order):**

1. Wireshark Basics - HTTP Traffic  
2. TCP Handshake Analysis  
3. DNS Query Investigation  
4. FTP Credential Extraction  
5. ICMP Packet Analysis  
6. Network Protocol Identification  
7. TCP Handshake Count  
8. TCP Fragmentation  
9. HTTPS/TLS Analysis  
10. Network Forensics - Data Exfiltration  

## 2.5 Core Application Logic (`app.py`)

**Helpers**

- **`check_and_award_badges(user_id, challenge_id)`**: After a correct flag submission, loads user’s completed challenges and earned badges. For each badge not yet earned, checks challenges_completed (total ≥ requirement_value) or daily_challenges (distinct challenges completed today ≥ requirement_value). Awards and returns list of newly awarded badges.
- **`get_unlocked_challenges(challenges, completed_ids)`**: Challenge 1 always unlocked; challenge N (N>1) unlocked iff challenge N-1 is in completed_ids.
- **`@login_required`**: Redirects to login if `'user_id'` not in session.

**Routes**

- **`/`**: If logged in → redirect to **home**; else → redirect to **login**.
- **`/register` (GET/POST)**: GET shows form. POST: validate name, email, password, confirm_password; on success hash password, create_user, set session, redirect to home. On duplicate email, show “Email already exists”.
- **`/login` (GET/POST)**: POST: get user by email; if exists and password matches, set session and redirect to home; else “Invalid email or password”.
- **`/logout`**: session.clear(), redirect to login.
- **`/api/me`** (GET, login_required): Returns JSON **`{ points, badges }`** (total points and count of badges earned). Used by the navbar to show points without reloading the page.
- **`/home`** (login_required): Loads user badges, total badges, **total_points** (via `get_user_total_points`), renders **home.html** (welcome, stats strip, achievements/badges, link to challenges).
- **`/challenges/network`** (login_required): Loads all challenges, user progress (completed_ids), **total_points**, computes **unlocked**, loads user badges and total badges, renders **dashboard.html** with challenges, completed_ids, unlocked, category “Network Security”, badges, total_points.
- **`/challenge/<int:challenge_id>`** (login_required): Validates challenge_id ≥ 1. Loads challenge; if not found, redirects to network challenges. Computes unlocked; if **challenge_id not in unlocked**, redirects to challenges list. Sets `is_completed = (challenge_id in completed_ids)`. Renders **challenge.html** with challenge, is_completed, category_url.
- **`/submit_flag`** (POST, login_required): Expects JSON: **`challenge_id`, `flag`, `used_hint`** (optional, boolean). Validates challenge_id and loads challenge. Normalizes and compares flag to stored flag. If correct: computes **points_earned** (base points from challenge, or half if used_hint); if not already completed, calls **`complete_challenge(conn, user_id, challenge_id, used_hint=used_hint, points_earned=points_earned)`**, then `check_and_award_badges`; returns JSON `{ success: true, message (incl. +X points), new_badges, points_earned }`. If wrong: `{ success: false, message: 'Incorrect flag. Try again!' }`. Frontend sends `used_hint` based on whether the user clicked “Show hint” before submitting.

There is no separate `/dashboard` route; the challenges dashboard is **`/challenges/network`**. Hints are rendered in the challenge page; there is no `/get_hint` API (hint visibility is toggled in the browser).

## 2.6 Frontend (Templates and JS)

**Base template (`base.html`)**

- Layout: navbar (brand “Thaghrah” linking to index; if logged in: Home, Challenges, stats [points from `/api/me`, email], Logout), main content block, footer. Uses `session.get('user_id')`. Includes Google Fonts (Outfit, JetBrains Mono), `style.css`, `main.js`, `challenge.js`, and optional `extra_scripts`. When logged in, a small script fetches `/api/me` and sets the nav points display.

**Home (`home.html`)**

- Hero (logo, “Thaghrah”, tagline, welcome message). If user_badges/total_points defined: **stats strip** (Points, Badges X/Y). **Achievements** panel: “Your Achievements”, badge count, total points, grid of earned badges (or “Complete challenges to earn badges and points”). **Challenge selection**: “Network Security Challenges”, subtitle, “View challenges” button → `/challenges/network`.

**Dashboard (`dashboard.html`) — URL: `/challenges/network`**

- Back link to home, logo, category title, short description. **Stats row**: Challenges (X/Y), Points, Badges (X/Y). **Progress card**: “Progress”, “X of Y completed”, progress bar. Optional **badges panel** (only if user has at least one badge). **Challenges** section: grid of challenge cards. Each card: title, short description, status badge (**✓ Completed** / Start / Locked). Unlocked: “Start challenge” → `/challenge/<id>`. Locked: disabled “Complete previous” button.

**Challenge page (`challenge.html`)**

- Back link to challenges, challenge title. If completed: success alert “You’ve completed this challenge.” **Sections**: Expected outcome, Description; for challenge IDs 1–8: Capture file (download pcap link); Hint (button toggles hint text; note that using hint reduces points); Submit flag (points note: full vs half points), form (hidden challenge_id, **used_hint** set by JS when user clicks “Show hint”), flag input, submit button, result div. On submit: JS sends POST `/submit_flag` with **`challenge_id`, `flag`, `used_hint`**. On success: show message (incl. +X points), optional badge alert, redirect to challenges (or home). On failure: show error, re-enable submit.

**Static assets**

- **static/css/style.css**: Layout, cards, forms, buttons, progress bar, nav, stats, badges, challenge cards (Completed/Unlocked/Locked), alerts. Variables for accent (cyan), error (red), success (cyan).
- **static/js/main.js**, **static/js/challenge.js**: Global and challenge-specific behavior; challenge page also uses inline script in `extra_scripts` for hint toggle and flag form (including `used_hint`).
- **static/pcaps/**: Pcap files (e.g. challenge_01.pcapng … challenge_08.pcapng) served as static files for download.

## 2.7 Flow Summary for an Auditor

1. **Startup**: `init_db()` applies schema, runs migrations (add points/used_hint/points_earned if missing), inserts badges and challenges if tables are empty.
2. **Auth**: Any `@login_required` view checks `session['user_id']`.
3. **Challenge list**: Unlock logic is server-side from DB + user_progress; no client-side bypass.
4. **Challenge page**: Rendered only if `challenge_id` is in the server-computed **unlocked** list.
5. **Flag submission**: Server-side comparison only (normalized); completion stored with **used_hint** and **points_earned**; badges checked; response is JSON (success, message with +points, new_badges).
6. **Points**: Stored per completion in user_progress; total points derived by SUM(points_earned); full vs half points based on hint usage at submit time.
7. **Passwords**: Only hashes stored; Werkzeug for hashing and checking.
8. **Session**: Secret key for signing; session holds user_id, email, name. No flags or sensitive challenge data in session.

This gives an audit-ready picture of how Thaghrah works and how each part of the code supports that behavior.
