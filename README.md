# Thaghrah

**Hands-on cybersecurity learning with packet captures.**  
A senior-project web app where students analyze PCAPS, submit flags, and progress through a guided curriculum—plus an optional AI Lab that generates new challenges from plain-language prompts.

## Quick start

From the project root (after cloning):

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python run.py
```

Open **http://127.0.0.1:5001**. First run creates the SQLite database and seeds challenges.

---

## What it does

| | |
|---|---|
| **Goal** | Structured practice with **Wireshark** and common protocols—not just reading about them. |
| **Curriculum** | **40 challenges** in **8 categories**: HTTP, TCP, DNS, FTP, ICMP, SMTP, TLS, forensics (5 each). |
| **Progress** | Challenges unlock in **one global order** so difficulty stays predictable. |
| **Scoring** | Correct flag = full points; **hints** cost half points on that challenge. |
| **AI Lab** | Logged-in users can describe a scenario; the backend builds a **downloadable PCAP**, objective, hint, and flag (needs API keys). |

---

## Features

- **Accounts** — Register, login, Werkzeug-hashed passwords (policy: 8+ chars, uppercase, special character).
- **Category pages** — Short protocol context (purpose, ports, why analysts care) plus challenge lists.
- **Badges** — Milestones as you complete challenges.
- **Completion** — Solving the last network challenge shows a **celebration modal**; dismiss with **Return to home**.
- **Logging** — Rotating `logs/app.log` for request timing and flag-submit outcomes (flags themselves are not logged).

---

## Tech stack

| | |
|---|---|
| Backend | Flask (Python) |
| DB | SQLite (`thaghrah.db`, created on startup) |
| Frontend | Jinja2, CSS, JavaScript |
| AI Lab | xAI Grok or Groq via HTTP API; PCAP build with Scapy |
| Tooling | Scapy, Pillow (captures / assets) |

Configuration uses `.env` via `python-dotenv` (see `thaghrah/core/config.py`).

---

## Prerequisites

- **Python 3.8+**
- **Wireshark** (or any tool that opens `.pcap` / `.pcapng`) for challenges
- **AI Lab (optional):** API key for Grok or Groq

---

## Configuration (AI Lab)

Copy `.env.example` to `.env` and set:

| Variable | Purpose |
|----------|---------|
| `GROK_API_KEY` | xAI or Groq API key |
| `GROK_PROVIDER` | `xai` or `groq` |
| `GROK_MODEL` | Model ID for that provider |
| `GROK_MAX_COMPLETION_TOKENS` | Optional token cap |


---

## Using the app

1. **Register** → **Log in**
2. Open the **next unlocked** challenge (fixed sequence).
3. **Download the PCAP**, analyze in Wireshark, **submit the flag**.
4. Use **hints** only if you’re okay with half points on that challenge.
5. Try **AI Lab** (`/challenges/ai`) if configured.

---

## Project layout

```
Senior-Project/
├── run.py                 # Dev server (port 5001)
├── requirements.txt
├── schema.sql
├── .env.example
├── thaghrah/              # App package (routes, db, auth, AI pipeline)
├── challenges/            # Challenge definitions by category
├── scripts/               # PCAP helpers, sync_challenges_to_db.py
├── templates/
└── static/
    ├── pcaps/             # Challenge + AI-generated captures
    └── keys/              # Demo TLS material (learning only)
```

After editing challenge metadata in `challenges/`, sync the DB without wiping users:

```bash
python scripts/sync_challenges_to_db.py
```

Challenge captures belong under `static/pcaps/` (see `scripts/` for generators). `logs/` is created at runtime.

---

## Learning outcomes

Students practice filtering and streams in Wireshark, relate protocols to real traffic, and optionally try **prompt-to-PCAP** workflows—useful prep before deeper security coursework.

---
## License

Educational project for cybersecurity learning.
