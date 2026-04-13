# Thaghrah — Cybersecurity Learning Platform

## Project description

**Thaghrah** is a web-based learning platform for **introductory cybersecurity**, built as a senior project. It addresses a common gap in early curricula: students read about protocols and tools, but rarely get enough **structured, repeatable practice** reading real packets. The platform turns packet analysis into a guided game—each challenge ships with a capture file (or instructions to produce one), a clear learning goal, and a flag to find—so learners build confidence with **Wireshark** and common **network protocols** without touching live production traffic.

Students register, work through **forty challenges** grouped into **eight categories** (HTTP, TCP, DNS, FTP, ICMP, SMTP, TLS, and network forensics). Short **category pages** explain what each protocol is for, typical ports, and why analysts care. Challenges unlock in a **fixed global order** so difficulty and prerequisites stay predictable. The app tracks **completion, points, and badges**: correct flags earn full credit, while optional **hints** trade guidance for half points—encouraging honest effort without leaving students stuck.

The system is implemented as a **Flask** application with **SQLite** for users, progress, and challenge metadata, **server-side sessions**, and **Werkzeug**-hashed passwords, plus optional **SMTP** for password reset. The front end uses **Jinja2** templates with custom CSS and JavaScript. Supporting **Python scripts** (often using **Scapy**) help authors generate or document packet captures under `static/pcaps/`. Together, Thaghrah is a self-contained environment for **safe, hands-on network security education**.

**One-line summary (for GitHub, forms, or abstracts):**  
*Thaghrah is a Flask-based cybersecurity learning platform where students analyze packet captures across eight protocol categories, submit flags, and earn points and badges in a sequential, classroom-friendly challenge track.*

## Features

- **User accounts**: Registration (name, email, password), login, and session handling
- **Password policy**: At least 8 characters, one uppercase letter, and one special character
- **Forgot password**: Request a reset link by email; use the link to set a new password (or see the link in the server console if SMTP is not configured)
- **40 network challenges** organized into **eight protocol categories** (five challenges each):
  - **HTTP** — traffic basics, headers, status codes, cookies, redirects
  - **TCP** — ports, handshakes, fragmentation, reassembly, port knocking
  - **DNS** — queries, TXT/CNAME records, chunked or encoded answers
  - **FTP** — control channel, credentials, data channel, file operations
  - **ICMP** — echo, types/codes, diagnostics and mixed traffic
  - **SMTP** — mail flow, commands, and related analysis
  - **TLS** — handshakes, certificates, ciphers, and encrypted session details
  - **Forensics** — multi-protocol investigation and exfiltration-style scenarios
- **Category pages**: Short protocol overviews (what it does, common ports, why it matters) plus a per-category challenge list
- **Progress**: Global unlock order—you complete challenges **in sequence** (the next challenge unlocks when the previous one is solved)
- **Points**: Full points for a correct flag without using the hint; **half points** if you used the hint for that challenge
- **Badges**: Earned at completion milestones (e.g. first challenge, halfway, all challenges)
- **Hints**: Optional per-challenge guidance without giving away the flag outright
- **UI**: Responsive HTML/CSS/JS with a dashboard and challenge detail pages

## Technology Stack

| Layer | Technologies |
|--------|----------------|
| Backend | [Flask](https://flask.palletsprojects.com/) (Python) |
| Database | SQLite (`thaghrah.db`, created/updated on startup) |
| Auth | Werkzeug password hashing; Flask sessions |
| Frontend | Jinja2 templates, CSS, JavaScript |
| Tooling | [Scapy](https://scapy.net/) and [Pillow](https://python-pillow.org/) (used in the repo for capture generation and assets where applicable) |

## Prerequisites

- **Python 3** (3.8 or newer recommended)
- **Wireshark** (or another tool that reads `.pcap` / `.pcapng`) for analyzing challenge captures
- Optional: **dumpcap** / **tshark** / **tcpdump** if you run scripts that record live traffic into `static/pcaps/`

## Installation

1. **Clone the repository** and enter the project directory.

2. **Create a virtual environment** (recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:

   ```bash
   python app.py
   ```

   On first run this initializes the SQLite schema, seeds categories/challenges/badges, and starts the development server.

5. **Open the app** at [http://127.0.0.1:5001](http://127.0.0.1:5001).

### Capture files (`static/pcaps/`)

Challenge pages expect packet captures under `static/pcaps/` (for example `challenge_01.pcapng`). The repository includes **scripts** that generate or help you record many of these files; if a file is missing locally, generate it with the matching script or add your own capture that matches the challenge spec. See `scripts/` for one-off generators (often documented in each script’s module docstring).

### Optional — email for password reset

For real email delivery (e.g. production), set:

| Variable | Example / notes |
|----------|------------------|
| `MAIL_SERVER` | `smtp.gmail.com` |
| `MAIL_PORT` | `587` |
| `MAIL_USE_TLS` | `1` for TLS |
| `MAIL_USERNAME` | SMTP username |
| `MAIL_PASSWORD` | App password or SMTP secret |
| `MAIL_FROM` | Sender address, e.g. `noreply@yourdomain.com` |

If `MAIL_SERVER` is unset, the reset link is **printed to the console** so you can test forgot-password locally.

## Developing and syncing challenge metadata

Challenge definitions live in Python modules under `challenges/<category>/challenge_XX.py`. If you edit titles, descriptions, hints, flags, or ordering fields, refresh the database copy without wiping user progress:

```bash
python scripts/sync_challenges_to_db.py
```

Run this from the **project root** so imports resolve correctly.

## Usage

1. **Register** with your name, email, and password.
2. **Log in** to reach the home/dashboard flow.
3. **Forgot password** (optional): From the login page, request a reset and follow the link (or copy it from the terminal if SMTP is off).
4. **Pick the next unlocked challenge**—you can browse by protocol category on the dashboard, but a **challenge page** only opens when that challenge is unlocked in the fixed global sequence.
5. **Download the pcap**, analyze it in Wireshark, and **submit the flag**.
6. **Use hints sparingly** if you want full points.

## Project structure

```
Senior-Project/
├── app.py                    # Flask app, routes, DB init, badge logic
├── db_queries.py             # SQLite helpers
├── schema.sql                # Reference schema (DB is also created in app.py)
├── requirements.txt
├── thaghrah.db               # SQLite database (created on first run)
├── scripts/                  # Pcap generators and sync utilities
│   └── sync_challenges_to_db.py
├── challenges/               # One folder per protocol category
│   ├── __init__.py           # Registers all challenges in global order
│   ├── http/
│   ├── tcp/
│   ├── dns/
│   ├── ftp/
│   ├── icmp/
│   ├── smtp/
│   ├── tls/
│   └── forensics/
├── templates/
│   ├── base.html
│   ├── start.html
│   ├── home.html
│   ├── dashboard.html
│   ├── category_challenges.html
│   ├── challenge.html
│   ├── login.html
│   ├── register.html
│   ├── forgot_password.html
│   └── reset_password.html
└── static/
    ├── css/
    ├── js/
    ├── pcaps/                # Challenge captures (.pcap / .pcapng); often generated locally
    └── keys/                 # TLS-related demo material for some challenges
```

## Learning outcomes

Working through Thaghrah helps students:

- Use Wireshark confidently for filtering, following streams, and reading common protocols
- Relate **HTTP, TCP, DNS, FTP, ICMP, SMTP, and TLS** to what they see on the wire
- Practice **forensics-style** reasoning across multiple signals in one capture
- Build disciplined flag-submission and documentation habits before advanced security courses

## Requirements summary

- Python 3.x with dependencies from `requirements.txt`
- A modern browser
- Wireshark (or equivalent) for opening challenge captures

## Notes

- The database is initialized automatically when you run `app.py`.
- Passwords are stored as Werkzeug hashes, not plaintext.
- Unlocking is **global and sequential** according to the order in `challenges/__init__.py`.
- Points and badge progress are stored per user.
- SMTP/TLS demo keys under `static/keys/` are for learning scenarios only—do not reuse as production secrets.

## License

Educational project for cybersecurity learning.
