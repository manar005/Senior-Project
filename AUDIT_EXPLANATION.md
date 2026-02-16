# Thaghrah 


# Part 1: Project Logic

## 1.1 Purpose

**Thaghrah** is an educational, web-based cybersecurity learning platform for first-year students. It is a **game-like** environment where users:

1. Create an account and log in.
2. Work through **10 network security challenges** in order.
3. Analyze **pcap** (packet capture) files in **Wireshark** to find a **flag** for each challenge.
4. Submit the flag in the app to complete the challenge and unlock the next one.
5. Earn **badges** for milestones (e.g. first challenge, 3 challenges, 5 in one day).

So the core loop is: **Register → Login → Open challenge → Download pcap → Analyze in Wireshark → Submit flag → Unlock next challenge & possibly earn badges.**

## 1.2 High-Level Flow

```
User visits app
    → Not logged in: redirect to Login (or Register)
    → Logged in: redirect to Home

Home
    → Shows welcome, badges, link to "Network Security" challenges

Network Challenges (dashboard)
    → Lists 10 challenges with status: Locked / Unlocked / Completed
    → Only Challenge 1 is unlocked initially
    → Unlock rule: complete challenge N to unlock challenge N+1

Challenge page (e.g. /challenge/1)
    → Shows: Expected Outcome, Description, (optional) Download pcap, Hint, Submit Flag
    → User downloads pcap, uses Wireshark, finds flag, types it in, submits

Submit flag (POST /submit_flag)
    → Server compares submitted flag to stored flag (case-insensitive)
    → If correct: record completion in user_progress, check badges, return success
    → If wrong: return "Incorrect flag"

Badges
    → Awarded when user meets criteria (e.g. 1, 3, 5, 7, 10 challenges completed; or 3/5 challenges in one day)
    → Stored in user_badges; shown on Home and Dashboard
```

## 1.3 Data Model (Logic)

- **Users**: One row per account (id, name, email, password_hash). Passwords are hashed with Werkzeug; never stored in plain text.
- **Challenges**: 10 rows, one per challenge (title, description, hint, flag, expected_outcome, etc.). Content is loaded from Python files on first run and inserted into the DB.
- **User progress**: One row per (user, challenge) when a user completes a challenge. Used to show “Completed” and to compute unlock (complete N → unlock N+1).
- **Badges**: Fixed set of badge definitions (name, icon, requirement_type, requirement_value).
- **User badges**: One row per (user, badge) when a user earns a badge. Used to show “Your Badges” on Home/Dashboard.

## 1.4 Security-Related Logic

- **Authentication**: Login sets `session['user_id']` (and email/name). Protected routes use a `@login_required` decorator that redirects to login if `user_id` is not in session.
- **Flag verification**: Done on the server only. Stored flag is in the DB; comparison is `flag.strip().upper() == challenge['flag'].upper()` (case-insensitive).
- **Challenge access**: A user can only open a challenge if its ID is in the **unlocked** list (Challenge 1 always unlocked; others unlock after completing the previous one). If they hit `/challenge/5` without completing 4, they are redirected to the challenges list.
- **Passwords**: Stored as hashes (Werkzeug); never logged or sent to the client except during login (password sent over HTTPS in production).

---

# Part 2: Code in Detail

## 2.1 Technology Stack

- **Backend**: Flask (Python).
- **Frontend**: HTML templates (Jinja2), CSS, vanilla JavaScript.
- **Database**: SQLite (`thaghrah.db`), created and migrated via `schema.sql`.
- **Auth**: Werkzeug `generate_password_hash` / `check_password_hash`; session-based (server-side session, secret key).

## 2.2 Entry Point and Database Setup

**File: `app.py`**

- **`if __name__ == '__main__'`**: Calls `init_db()` then `app.run(debug=True, host='127.0.0.1', port=5001)`.
- **`init_db()`**:
  1. Opens a connection and runs the entire **`schema.sql`** script (creates tables if not exist).
  2. If no badges exist: inserts the 7 predefined badges (e.g. “First Steps”, “Getting Started”, …).
  3. If no challenges exist: calls **`get_network_challenges()`** from the `challenges` package, builds a list of rows (title, description, hint, flag, expected_outcome, challenge_type, challenge_data, order_num), and calls **`db_queries.insert_challenges(conn, challenge_data)`** to insert all 10 challenges.

So the **source of truth for challenge text and flags** is the Python files in `challenges/`; the DB is populated once at first run. Later changes to the Python files do not auto-update the DB (the app reads from the DB). To reflect edits to challenge content, the database would need to be updated manually or re-seeded (e.g. by re-running init_db on an empty DB, which would clear existing data).

- **`get_db()`**: Returns a SQLite connection with **`row_factory = sqlite3.Row`** so that query results behave like dicts (e.g. `row['email']`), used consistently in the app and in `db_queries`.

## 2.3 Database Layer

**File: `schema.sql`**

- Defines:
  - **users**: id, name, email (UNIQUE), password_hash, created_at.
  - **challenges**: id, title, description, hint, flag, expected_outcome, challenge_type, challenge_data, order_num.
  - **user_progress**: id, user_id, challenge_id, completed_at; UNIQUE(user_id, challenge_id); foreign keys to users and challenges.
  - **badges**: id, name, description, icon, requirement_type, requirement_value.
  - **user_badges**: id, user_id, badge_id, earned_at; UNIQUE(user_id, badge_id); foreign keys.

**File: `db_queries.py`**

- All functions take a **connection object `conn`** (and relevant IDs/values). The caller (app) is responsible for opening/closing the connection.
- **User**: `get_user_by_email`, `create_user` (returns new user id).
- **Challenges**: `get_all_challenges` (ordered by order_num), `get_challenge_by_id`, `get_challenge_count`, `insert_challenges` (batch insert).
- **Progress**: `get_user_progress` (list of challenge_id for a user), `check_challenge_completed`, `complete_challenge` (inserts into user_progress if not already completed; returns True/False).
- **Badges**: `get_all_badges`, `get_badge_count`, `get_user_badges` (badges earned by user), `get_user_badge_ids`, `get_total_badges_count`, `award_badge` (inserts into user_badges if not already awarded; returns True/False).

This keeps SQL and DB access in one place and makes the app code easier to audit and test.

## 2.4 Challenges Module

**File: `challenges/__init__.py`**

- Imports `challenge_01` … `challenge_10` (each module defines a dict named `challenge`).
- **`get_network_challenges()`** returns a list `[challenge_01, challenge_02, …]`. Order is fixed (1–10). Used by `init_db()` to seed the DB and by the sync script to update it.

**Files: `challenges/challenge_01.py` … `challenge_10.py`**

- Each defines a single dict **`challenge`** with keys such as: `title`, `description`, `hint`, `flag`, `expected_outcome`, `challenge_type`, `order_num` (and optionally `challenge_data`). The **flag** is the string the user must submit (after finding it via Wireshark/pcap analysis). The app does **not** read these files at runtime for display or validation; it uses the database. The Python files are for seeding and for the sync script.

## 2.5 Core Application Logic (`app.py`)

**Helpers**

- **`check_and_award_badges(user_id, challenge_id)`**: After a correct flag submission, loads user’s completed challenges and earned badges. For each badge not yet earned, checks:
  - **challenges_completed**: total completed count ≥ requirement_value (e.g. 1, 3, 5, 7, 10).
  - **daily_challenges**: count of distinct challenges completed **today** ≥ requirement_value (e.g. 3, 5).
  If the condition is met, calls `db_queries.award_badge` and appends to `new_badges`. Returns list of newly awarded badges.
- **`get_unlocked_challenges(challenges, completed_ids)`**: Given the ordered list of challenges and the set of completed challenge IDs, returns the list of challenge IDs that are unlocked: challenge 1 is always unlocked; challenge N (N>1) is unlocked if challenge N-1 is in `completed_ids`.
- **`@login_required`**: Decorator that redirects to `login` if `'user_id'` not in `session`; otherwise runs the view.

**Routes**

- **`/`**: If logged in (`user_id` in session) → redirect to **home**; else → redirect to **login**.
- **`/register` (GET/POST)**: GET shows the form. POST: validates name, email, password, confirm_password; if mismatch or missing fields, re-renders with error. On success: hash password, `create_user`, store `user_id`, `email`, `name` in session, redirect to home. On duplicate email (IntegrityError), show “Email already exists”.
- **`/login` (GET/POST)**: GET shows form. POST: get user by email; if user exists and `check_password_hash` matches, set session and redirect to home; else “Invalid email or password”.
- **`/logout`**: `session.clear()`, redirect to login.
- **`/home`** (login_required): Loads user badges and total badge count from DB, renders **home.html** (welcome, badges, link to challenges).
- **`/challenges/network`** (login_required): Loads all challenges, user progress (completed_ids), computes **unlocked** via `get_unlocked_challenges`, loads user badges and total badges, renders **dashboard.html** with challenges, completed_ids, unlocked, category “Network Security”, badges.
- **`/dashboard`** (login_required): Same as above but without category and without passing user_badges/total_badges (template can still show progress and challenge list).
- **`/challenge/<int:challenge_id>`** (login_required): Validates challenge_id ≥ 1. Loads challenge by ID; if not found, redirects to network challenges. Loads all challenges and user progress, computes unlocked. If **challenge_id not in unlocked**, redirects back to challenges list (no direct URL access to locked challenges). Sets `is_completed = (challenge_id in completed_ids)`. Renders **challenge.html** with challenge, is_completed, category_url (back link).
- **`/submit_flag` (POST, login_required)**: Expects JSON: `challenge_id`, `flag`. Validates presence and that challenge_id is a positive integer. Loads challenge from DB; if not found, 404. Compares **`flag.strip().upper() == challenge['flag'].upper()`**. If correct: checks whether already completed; if not, calls `complete_challenge` and then `check_and_award_badges`; returns JSON `{ success: true, message, new_badges }`. If wrong: returns `{ success: false, message: 'Incorrect flag. Try again!' }`. Frontend shows the message and, on success, can show badge alert and then redirect back to the challenges list.
- **`/get_hint` (POST, login_required)**: Expects JSON `challenge_id`. Returns `{ hint: challenge.hint }` or error if challenge not found. Used to provide hints without exposing the flag.

## 2.6 Frontend (Templates and JS)

**Base template (`base.html`)**

- Common layout: navbar (brand “Thaghrah”; if `session.user_id` then Home, Logout, user email), main block for content, footer. Includes `style.css`, `main.js`, `challenge.js`, and an optional `extra_scripts` block.

**Dashboard (`dashboard.html`)**

- Extends base. Shows “Back to Home”, category title (e.g. “Network Security”), progress summary (X/10 challenges), optional badges panel (if `user_badges` is defined), then a grid of **challenge cards**. Each card shows title, short description, and status (Completed / Unlocked / Locked). Only **unlocked** challenges get a “Start Challenge” link to `/challenge/<id>`; locked ones show a disabled “Complete previous challenge” button.

**Challenge page (`challenge.html`)**

- Extends base. Shows back link, challenge title, “Expected Outcome”, “Description”. For challenge IDs 1, 2, 3 it shows a “Download pcap” link to `static/pcaps/challenge_01.pcapng`, etc. Then “Hint” (button toggles visibility of hint text), “Submit Flag” (form with hidden challenge_id and text input for flag). On submit, JavaScript **prevents default**, sends **POST /submit_flag** with JSON `{ challenge_id, flag }`. On success: shows message, optional badge alert, then redirect to category URL (or home). On failure: shows “Incorrect flag. Try again!” (or error message). Hint is rendered server-side; no extra request needed for the visible hint (get_hint exists for possible future use).

**Static assets**

- **static/css/style.css**: Styles for layout, cards, forms, buttons, progress bar.
- **static/js/main.js**, **static/js/challenge.js**: Global and challenge-specific behavior (challenge page uses inline script in `extra_scripts` for the form and hint toggle).
- **static/pcaps/**: Holds pcap files (e.g. challenge_01.pcapng, challenge_02.pcapng, challenge_03.pcapng) served by Flask as static files; users download them to analyze in Wireshark.

## 2.7 Flow Summary for an Auditor

1. **Startup**: `app.py` runs `init_db()`: schema applied, badges and challenges inserted if tables are empty.
2. **Request**: Each request (except login/register) that hits a `@login_required` view is checked for `session['user_id']`.
3. **Challenge list**: Challenges and unlock logic come from DB + `user_progress`; no client-side bypass (server recomputes unlocked on each load).
4. **Challenge page**: Only rendered if `challenge_id` is in the server-computed **unlocked** list.
5. **Flag submission**: Only server-side comparison with DB flag; case-insensitive; completion and badges updated in DB; response is JSON (success/message and optional new_badges).
6. **Passwords**: Only hashes stored; Werkzeug used for hashing and checking.
7. **Session**: Secret key for signing; session holds user_id, email, name. No sensitive data (e.g. flag) stored in session.

This should give you a clear, audit-ready picture of how Thaghrah works and how each part of the code supports that behavior.
