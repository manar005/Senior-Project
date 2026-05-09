# Thaghrah — Cybersecurity Learning Platform

## Project description

**Thaghrah** is a web-based learning platform for **introductory cybersecurity**, built as a senior project. It addresses a common gap in early curricula: students read about protocols and tools, but rarely get enough **structured, repeatable practice** reading real packets. The platform turns packet analysis into a guided game—each challenge ships with a capture file (or instructions to produce one), a clear learning goal, and a flag to find—so learners build confidence with **Wireshark** and common **network protocols** without touching live production traffic.

Students register, work through **forty curated challenges** grouped into **eight categories** (HTTP, TCP, DNS, FTP, ICMP, SMTP, TLS, and network forensics). Short **category pages** explain what each protocol is for, typical ports, and why analysts care. Challenges unlock in a **fixed global order** so difficulty and prerequisites stay predictable. The app tracks **completion, points, and badges**: correct flags earn full credit, while optional **hints** trade guidance for half points—encouraging honest effort without leaving students stuck.

Beyond the fixed curriculum, **AI Lab** lets authenticated users describe a scenario in plain language. An LLM-backed pipeline proposes a unique challenge plan; the server materializes a **downloadable PCAP**, learning objective, hint, and flag so learners can practice analysis with fresh traffic. Completing **all forty network challenges** triggers a **full-screen celebration** (confetti and congratulations) with a **Return to home** action—no timed redirect, so the learner can dismiss when ready.

The system is implemented as a **Flask** application with **SQLite** for users, progress, AI challenge rows, and challenge metadata, **server-side sessions**, and **Werkzeug**-hashed passwords. The front end uses **Jinja2** templates with custom CSS and JavaScript. Supporting **Python scripts** (often using **Scapy**) help authors generate or document packet captures under `static/pcaps/`. **Structured request logging** (rotating file under `logs/`) helps operators trace flag submission latency and completion flows during development or demos. Together, Thaghrah is a self-contained environment for **safe, hands-on network security education**.

**One-line summary (for GitHub, forms, or abstracts):**  
*Thaghrah is a Flask-based cybersecurity learning platform where students analyze packet captures across eight protocol categories, optionally generate AI-assisted PCAP challenges, submit flags, earn points and badges in a sequential track, and finish with a celebratory completion experience.*

## Features

- **User accounts**: Registration (name, email, password), login, and session handling
- **Password policy**: At least 8 characters, one uppercase letter, and one special character
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
- **Grand finale**: When the **last** of the 40 network challenges is solved correctly, a modal celebrates completion with confetti; the user closes it with **Return to home** (navigates to the home page)
- **AI Lab** (`/challenges/ai`): Prompt-driven generation of a unique PCAP challenge per request, with download, optional hint (half points if used), and flag submission integrated with the same points model
- **Developer-friendly logging**: Rotating `logs/app.log` records request timing and flag-submit outcomes (without logging raw flags) for troubleshooting UX and latency
- **UI**: Responsive HTML/CSS/JS with a dashboard, challenge detail pages, and AI lab workspace

## Technology Stack

| Layer | Technologies |
|--------|----------------|
| Backend | [Flask](https://flask.palletsprojects.com/) (Python) |
| Database | SQLite (`thaghrah.db`, created/updated on startup) |
| Auth | Werkzeug password hashing; Flask sessions |
| Frontend | Jinja2 templates, CSS, JavaScript |
| Configuration | `.env` loading via `python-dotenv` with a fallback loader in `thaghrah/core/config.py` |
| AI challenge pipeline | HTTP APIs (xAI Grok or Groq, selectable via env); JSON plan → PCAP build (`thaghrah.ai.pcap_plan`, Scapy / optional tshark path) |
| Logging | Python `logging` with `RotatingFileHandler` → `logs/app.log` |
| Tooling | [Scapy](https://scapy.net/) and [Pillow](https://python-pillow.org/) (capture generation and assets where applicable) |

## Prerequisites

- **Python 3** (3.8 or newer recommended)
- **Wireshark** (or another tool that reads `.pcap` / `.pcapng`) for analyzing challenge captures
- Optional: **dumpcap** / **tshark** / **tcpdump** if you run scripts that record live traffic into `static/pcaps/`
- **AI Lab**: A valid API key for **xAI Grok** or **Groq** (see environment variables below)

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

4. **Configure environment (recommended for AI Lab)**:

   Copy `.env.example` to `.env` in the project root and set at least:

   | Variable | Purpose |
   |----------|---------|
   | `GROK_API_KEY` | API key from xAI or Groq (same variable name in app) |
   | `GROK_PROVIDER` | `xai` or `groq` — selects which API to call |
   | `GROK_MODEL` | Model id accepted by that provider |
   | `GROK_MAX_COMPLETION_TOKENS` | Optional cap on completion tokens (helps stay within rate limits) |

   `.env` is gitignored; never commit real secrets.

5. **Run the application**:

   ```bash
   python run.py
   ```

   On first run this initializes the SQLite schema, seeds categories/challenges/badges, and starts the development server.

6. **Open the app** at [http://127.0.0.1:5001](http://127.0.0.1:5001).

### Capture files (`static/pcaps/`)

Challenge pages expect packet captures under `static/pcaps/` (for example `challenge_01.pcapng`). The repository includes **scripts** that generate or help you record many of these files; if a file is missing locally, generate it with the matching script or add your own capture that matches the challenge spec. See `scripts/` for one-off generators (often documented in each script’s module docstring). AI-generated captures are stored under `static/pcaps/` with unique filenames.

### Logs (`logs/`)

On startup the app ensures `logs/` exists and writes **rotating** logs to `logs/app.log` (with numbered backups when the file grows large). Useful lines include HTTP timing for `/submit_flag` and `/challenges/ai/*`, plus structured submit outcomes. Adjust verbosity or handlers in `thaghrah/__init__.py` if you deploy to production.

## Developing and syncing challenge metadata

Challenge definitions live in Python modules under `challenges/<category>/challenge_XX.py`. If you edit titles, descriptions, hints, flags, or ordering fields, refresh the database copy without wiping user progress:

```bash
python scripts/sync_challenges_to_db.py
```

Run this from the **project root** so imports resolve correctly.

## Usage

1. **Register** with your name, email, and password.
2. **Log in** to reach the home/dashboard flow.
3. **Pick the next unlocked challenge**—you can browse by protocol category on the dashboard, but a **challenge page** only opens when that challenge is unlocked in the fixed global sequence.
4. **Download the pcap**, analyze it in Wireshark, and **submit the flag**.
5. **Use hints sparingly** if you want full points.
6. **AI Lab** (optional): From the nav, open **AI lab**, describe a scenario, generate a challenge, download the PCAP, and submit the flag when ready.

## Project structure

```
Senior-Project/
├── run.py                    # Dev entrypoint: DB init + Flask dev server
├── thaghrah/                 # Application package
│   ├── __init__.py           # create_app(), logging, request timing
│   ├── core/                 # Paths, `.env`, protocol category IDs (`PROTOCOL_NAMES` in `constants.py`)
│   ├── content/              # Guide, cheat-sheet, protocol blurbs (`protocol_details.py`) — no Flask
│   ├── domain/               # Challenge progression, flags, badges
│   ├── ai/                   # Grok client, validation, PCAP build, AI hint helpers
│   ├── db/                   # `database.py` (migrations), `queries.py`
│   ├── auth/                 # `login_required` and related
│   └── routes/               # HTTP handlers only
├── schema.sql                # Reference schema (DB is created/updated in init_db)
├── requirements.txt
├── .env.example              # Template for API keys (copy to .env)
├── thaghrah.db               # SQLite database (created on first run)
├── logs/                     # Created at runtime; app.log (+ rotations)
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
│   ├── challenge.html        # Includes grand-finale modal after all 40 solved
│   ├── ai_challenge.html     # AI Lab UI
│   ├── login.html
│   ├── register.html
│   └── ...
└── static/
    ├── css/
    ├── js/
    ├── pcaps/                # Challenge captures + AI-generated PCAPs
    └── keys/                 # TLS-related demo material for some challenges
```

## Learning outcomes

Working through Thaghrah helps students:

- Use Wireshark confidently for filtering, following streams, and reading common protocols
- Relate **HTTP, TCP, DNS, FTP, ICMP, SMTP, and TLS** to what they see on the wire
- Practice **forensics-style** reasoning across multiple signals in one capture
- Optionally experience **prompt-to-PCAP** workflows that mirror tool-assisted analysis and scenario authoring
- Build disciplined flag-submission and documentation habits before advanced security courses

## Requirements summary

- Python 3.x with dependencies from `requirements.txt`
- A modern browser
- Wireshark (or equivalent) for opening challenge captures
- For AI Lab: provider API key and network access to that API

## Notes

- The database is initialized automatically when you run `run.py`.
- Passwords are stored as Werkzeug hashes, not plaintext.
- Unlocking is **global and sequential** according to the order in `challenges/__init__.py`.
- Points and badge progress are stored per user.
- SMTP/TLS demo keys under `static/keys/` are for learning scenarios only—do not reuse as production secrets.

## License

Educational project for cybersecurity learning.
