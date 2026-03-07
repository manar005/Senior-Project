"""One-off script for Challenge 15 pcap.
Redirect chain uses non-obvious path names; /about and /help (and similar) are
sent in between redirect steps so the chain is spread across multiple TCP streams.
Client does not follow redirects—each request is a separate connection.

Run while capturing on loopback in Wireshark; save as static/pcaps/challenge_15.pcapng.
"""
import http.server
import socketserver
import threading
import time
import http.client

HOST = "127.0.0.1"
PORT = 8779  # Avoid conflict with challenge 14 (8778)
FLAG = "REDIRECT_FINAL"


class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        # Noise: plain 200 responses, no redirect, no flag
        if path == "/":
            self._send_plain(200, b"OK\n")
            return
        if path == "/about":
            self._send_plain(200, b"About page.\n")
            return
        if path == "/contact":
            self._send_plain(200, b"Contact.\n")
            return
        if path == "/help":
            self._send_plain(200, b"Help.\n")
            return
        if path == "/support":
            self._send_plain(200, b"Support.\n")
            return
        if path == "/products":
            self._send_plain(200, b"Products.\n")
            return
        if path == "/blog":
            self._send_plain(200, b"Blog.\n")
            return
        if path == "/register":
            self._send_plain(200, b"Register.\n")
            return
        if path == "/search":
            self._send_plain(200, b"Search.\n")
            return
        # Redirect chain (obscure names; final path is /result, not "flag")
        if path == "/entry":
            self.send_response(302)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Location", "/phase2")
            self.end_headers()
            self.wfile.write(b"Moved.\n")
            return
        if path == "/phase2":
            self.send_response(302)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Location", "/verify")
            self.end_headers()
            self.wfile.write(b"Moved.\n")
            return
        if path == "/verify":
            self.send_response(302)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Location", "/result")
            self.end_headers()
            self.wfile.write(b"Moved.\n")
            return
        if path == "/result":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("X-Flag", FLAG)
            self.end_headers()
            self.wfile.write(b"Done.\n")
            return
        self.send_response(404)
        self.end_headers()

    def _send_plain(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_server():
    with socketserver.TCPServer((HOST, PORT), RedirectHandler) as httpd:
        httpd.serve_forever()


def client_requests():
    time.sleep(0.3)
    # Each request is a new connection so we get separate TCP streams.
    # Order: chain step, noise, chain step, noise, ... per user spec.
    requests = [
        "/entry",    # 302 → /phase2
        "/about",    # noise
        "/help",     # noise
        "/phase2",   # 302 → /verify
        "/contact",  # noise
        "/support",  # noise
        "/products", # noise
        "/verify",   # 302 → /result
        "/blog",     # noise
        "/register", # noise
        "/result",   # 200 with X-Flag
        "/search",   # noise
    ]
    for path in requests:
        try:
            conn = http.client.HTTPConnection(HOST, PORT, timeout=2)
            conn.request("GET", path)
            resp = conn.getresponse()
            resp.read()  # drain body so it appears in capture
            conn.close()
        except Exception:
            pass
        time.sleep(0.02)
    time.sleep(0.2)


if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    client_requests()
