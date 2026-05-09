"""One-off script for Challenge 14 pcap.
Simulates HTTP login: several POST /login attempts; one succeeds and the server
responds with 200 and Set-Cookie: session=COOKIE_SESSION_FLAG.
Solver must find the successful response and submit the cookie value as the flag.

Run while capturing on loopback in Wireshark; save as static/pcaps/challenge_04.pcapng.
"""
import http.server
import socketserver
import threading
import time
import urllib.parse
import http.client

HOST = "127.0.0.1"
PORT = 8778  # Avoid conflict with challenge 12 (8776), 13 (8777)
USERNAME = "admin"
CORRECT_PASSWORD = "secret123"
# Flag is the session cookie value set on successful login
SESSION_COOKIE_FLAG = "COOKIE_SESSION_FLAG"

# Wrong passwords, then one success, then one more wrong
PASSWORD_ATTEMPTS = [
    "wrong",
    "password",
    "123456",
    CORRECT_PASSWORD,  # 4th attempt – success, server sets Set-Cookie
    "guest",
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
            # Flag is the cookie value – solver extracts this from Set-Cookie
            self.send_header(
                "Set-Cookie",
                "session=%s; Path=/; HttpOnly" % SESSION_COOKIE_FLAG,
            )
            self.end_headers()
            self.wfile.write(b"Login successful. Session started.\n")
        else:
            self.send_response(401)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Invalid credentials.\n")

    def log_message(self, format, *args):
        return


def run_server():
    with socketserver.TCPServer((HOST, PORT), LoginHandler) as httpd:
        httpd.serve_forever()


def client_requests():
    time.sleep(0.3)
    for pwd in PASSWORD_ATTEMPTS:
        conn = http.client.HTTPConnection(HOST, PORT, timeout=2)
        body = urllib.parse.urlencode({"username": USERNAME, "password": pwd})
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            conn.request("POST", "/login", body=body, headers=headers)
            resp = conn.getresponse()
            resp.read()
        except OSError:
            pass
        finally:
            conn.close()
        time.sleep(0.05)
    time.sleep(0.2)


if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    client_requests()
