"""One-off script for Challenge (Forensics HTTP brute; pcap suffix 37) pcap.
Simulates an HTTP login brute-force attack against a simple /login endpoint.
Several POST attempts with wrong passwords are made; one attempt succeeds.
Solver must analyze the HTTP traffic, find the successful login, and extract
the correct password (flag).

Run while capturing on loopback in Wireshark; save as static/pcaps/challenge_37.pcapng.
"""
import http.server
import socketserver
import threading
import time
import urllib.parse
import http.client

HOST = "127.0.0.1"
PORT = 8081  # Avoid conflict with challenge 2 (8080)
USERNAME = "operator"
CORRECT_PASSWORD = "p@ssw0rd!"
# Several wrong, then one success, then two more wrong (success is not first/last)
PASSWORD_GUESSES = [
    "123456",
    "password",
    "letmein",
    "qwerty",
    CORRECT_PASSWORD,  # 5th attempt – only success
    "welcome",
    "monkey",
]


class LoginHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/login":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="ignore")
        params = urllib.parse.parse_qs(body)
        username = params.get("username", [""])[0]
        password = params.get("password", [""])[0]

        if username == USERNAME and password == CORRECT_PASSWORD:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(("Login successful. Welcome, %s!" % USERNAME).encode("utf-8"))
        else:
            self.send_response(401)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Invalid credentials.")

    def log_message(self, format, *args):
        # Silence console logging
        return


def run_server():
    with socketserver.TCPServer((HOST, PORT), LoginHandler) as httpd:
        # Handle requests until the client is done
        httpd.serve_forever()


def brute_force_client():
    time.sleep(0.3)  # Give server time to start
    for pwd in PASSWORD_GUESSES:
        conn = http.client.HTTPConnection(HOST, PORT, timeout=2)
        body = urllib.parse.urlencode({"username": USERNAME, "password": pwd})
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            conn.request("POST", "/login", body=body, headers=headers)
            resp = conn.getresponse()
            resp.read()  # Drain response body so it appears in capture
        except OSError:
            pass
        finally:
            conn.close()
        time.sleep(0.05)


def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    brute_force_client()
    # Give Wireshark a moment to capture the last packets
    time.sleep(0.2)


if __name__ == "__main__":
    main()

