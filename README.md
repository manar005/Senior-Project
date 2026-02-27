# Thaghrah - Cybersecurity Learning Platform

Thaghrah is an educational and interactive web-based game designed specifically for first-year cybersecurity students. The platform provides a safe and engaging environment for students to learn fundamental cybersecurity concepts through hands-on challenges.

## Features

- **User Authentication**: Secure registration and login system
- **Forgot Password**: Request a reset link by email; click the link to set a new password
- **10 Network Security Challenges**: Progressive network analysis challenges covering:
  - HTTP traffic analysis (Wireshark basics)
  - TCP handshake and port identification
  - DNS query investigation
  - FTP credential extraction
  - ICMP packet analysis
  - Network protocol identification
  - TCP handshake counting
  - TCP fragmentation and reassembly
  - HTTPS/TLS analysis
  - Network forensics and data exfiltration
- **Progress Tracking**: Track completed challenges and unlock new ones sequentially
- **Points System**: Earn points for each correct flag; full points without hints, 50% points if you use the hint
- **Badge System**: Earn badges for completing challenges and achieving milestones
- **Hints System**: Get guidance when stuck without spoiling the solution (using a hint reduces points for that challenge)
- **Modern UI**: Responsive and user-friendly interface

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Authentication**: Werkzeug password hashing

## Installation

1. **Clone or download the project**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```
   
   The application will automatically:
   - Initialize the database
   - Create challenge data
   - Set up badges and user progress tracking

4. **Access the application**:
   Open your browser and navigate to `http://127.0.0.1:5001`
   
   **Note**: You'll need Wireshark installed to analyze the pcap files for the network challenges.

**Optional – Email for forgot password**
To send reset links by email (e.g. in production), set these environment variables before running the app:

- `MAIL_SERVER` – SMTP server (e.g. `smtp.gmail.com`)
- `MAIL_PORT` – e.g. `587`
- `MAIL_USE_TLS` – `1` for TLS
- `MAIL_USERNAME` – SMTP username
- `MAIL_PASSWORD` – SMTP password or app password
- `MAIL_FROM` – Sender address (e.g. `noreply@yourdomain.com`)

If `MAIL_SERVER` is not set, the app still runs: the reset link is printed in the console so you can test forgot-password locally.

## Usage

1. **Register**: Create a new account with your email and password
2. **Login**: Sign in to access the dashboard
3. **Forgot password**: On the login page, click "Forgot password?", enter your email, then click the link in the email to set a new password
4. **Start Challenges**: Begin with Challenge 1 and work your way through
5. **Submit Flags**: Enter the correct flag to complete each challenge
6. **Unlock Progress**: Complete challenges sequentially to unlock the next one

## Challenge Types

All challenges focus on **Network Security** and require packet analysis using Wireshark:

1. **Wireshark Basics - HTTP Traffic**: Analyze web traffic, headers, and responses
2. **TCP Handshake Analysis**: Understand TCP handshakes, ports, and connections
3. **DNS Query Investigation**: Analyze DNS queries and encoded flags in domain names
4. **FTP Credential Extraction**: Extract credentials from FTP traffic (port 2121)
5. **ICMP Packet Analysis**: Understand ICMP packet types and purposes
6. **Network Protocol Identification**: Identify application-layer protocols (e.g., SMTP on port 2525)
7. **TCP Handshake Count**: Count complete three-way handshakes in a capture
8. **TCP Fragmentation**: Reassemble a flag split across multiple TCP streams (port 8888)
9. **HTTPS/TLS Analysis**: Examine TLS version and handshake in encrypted connections
10. **Network Forensics - Data Exfiltration**: Detect base64-encoded data in DNS subdomain queries

## Project Structure

```
Senior-Project/
├── app.py                 # Flask application
├── db_queries.py          # Database query helper functions
├── schema.sql             # Database schema definition
├── requirements.txt       # Python dependencies
├── thaghrah.db           # SQLite database (created on first run)
├── challenges/            # Network security challenges
│   ├── __init__.py
│   ├── challenge_01.py   # Wireshark Basics - HTTP Traffic
│   ├── challenge_02.py   # TCP Handshake Analysis
│   ├── challenge_03.py   # DNS Query Investigation
│   ├── challenge_04.py   # FTP Credential Extraction
│   ├── challenge_05.py   # ICMP Packet Analysis
│   ├── challenge_06.py   # Network Protocol Identification
│   ├── challenge_07.py   # TCP Handshake Count
│   ├── challenge_08.py   # TCP Fragmentation
│   ├── challenge_09.py   # HTTPS/TLS Analysis
│   └── challenge_10.py   # Network Forensics - Data Exfiltration
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── dashboard.html
│   └── challenge.html
└── static/               # Static files
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── main.js
    │   └── challenge.js
    └── images/
```

## Learning Outcomes

By completing Thaghrah's network security challenges, students will:
- Develop proficiency in using Wireshark for packet analysis
- Understand network protocols (HTTP, TCP, DNS, FTP, ICMP, TLS/SSL)
- Learn to extract credentials and identify protocols from traffic
- Practice TCP handshake recognition, fragmentation, and reassembly
- Analyze TLS/SSL handshakes and encrypted connection details
- Gain hands-on experience with DNS-based data exfiltration detection
- Build analytical thinking and problem-solving skills in cybersecurity
- Prepare for advanced network security and penetration testing courses

## Requirements

- **Python 3.x**: Required to run the Flask application
- **Wireshark**: Required for analyzing pcap files in network challenges
- **Web Browser**: Modern browser (Chrome, Firefox, Edge, etc.)

## Notes

- The database is automatically initialized on first run
- All passwords are securely hashed using Werkzeug
- Challenges must be completed in order (sequential unlocking)
- Progress and badges are saved per user account
- Each challenge awards points (e.g. 100) for a correct flag; using the hint before solving gives half points
- Pcap files for challenges need to be provided separately (not included in repository)

## License

Educational project for cybersecurity learning.
