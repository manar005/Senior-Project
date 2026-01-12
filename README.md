# Thaghrah - Cybersecurity Learning Platform

Thaghrah is an educational and interactive web-based game designed specifically for first-year cybersecurity students. The platform provides a safe and engaging environment for students to learn fundamental cybersecurity concepts through hands-on challenges.

## Features

- **User Authentication**: Secure registration and login system
- **10 Progressive Challenges**: Gradually increasing difficulty with various types:
  - Text-based encoding/decoding challenges
  - Image steganography
  - Cookie investigation
  - Source code inspection
- **Progress Tracking**: Track completed challenges and unlock new ones
- **Hints System**: Get guidance when stuck without spoiling the solution
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
   
   **Optional**: For better image support in Challenge 6, install Pillow:
   ```bash
   pip install Pillow
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```
   
   The application will automatically:
   - Initialize the database
   - Create challenge data
   - Generate the challenge image (if Pillow is installed)

4. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Register**: Create a new account with your email and password
2. **Login**: Sign in to access the dashboard
3. **Start Challenges**: Begin with Challenge 1 and work your way through
4. **Submit Flags**: Enter the correct flag to complete each challenge
5. **Unlock Progress**: Complete challenges sequentially to unlock the next one

## Challenge Types

- **Text Encoding**: Base64, ROT13, Hexadecimal, URL encoding, Binary, Morse code
- **Web Inspection**: Page source, cookies, browser developer tools
- **Image Analysis**: Steganography and metadata investigation
- **Logic Puzzles**: Pattern recognition and problem-solving

## Project Structure

```
Senior-Project/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── thaghrah.db           # SQLite database (created on first run)
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── challenge.html
└── static/               # Static files
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── main.js
    │   └── challenge.js
    └── images/
        └── hidden_message.png
```

## Learning Outcomes

By completing Thaghrah's challenges, students will:
- Develop an understanding of basic cybersecurity principles
- Practice problem-solving and analytical thinking
- Gain hands-on experience with simple cybersecurity scenarios
- Build confidence and curiosity to pursue further study in cybersecurity

## Notes

- The database is automatically initialized on first run
- All passwords are securely hashed using Werkzeug
- Challenges must be completed in order
- Progress is saved per user account

## License

Educational project for cybersecurity learning.
