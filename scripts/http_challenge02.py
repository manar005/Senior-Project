"""One-off script for Challenge (HTTP status; pcap suffix 02) pcap.
Serves a few HTTP requests: some return 200, one returns 404.
Solver finds the 404 response and submits STATUS_404.

Run while capturing on loopback in Wireshark; save as static/pcaps/challenge_02.pcapng.
"""
import http.server
import socketserver
import threading
import time
import urllib.request

HOST = "127.0.0.1"
PORT = 8776  # Avoid conflict with challenge 1 (8765)


class StatusHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK\n")
        elif self.path == "/missing":
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("X-Flag", "STATUS_404")
            self.end_headers()
            self.wfile.write(b"Not Found. Flag: STATUS_404\n")
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK\n")

    def log_message(self, format, *args):
        return


def run_server():
    with socketserver.TCPServer((HOST, PORT), StatusHandler) as httpd:
        httpd.serve_forever()


def client_requests():
    time.sleep(0.3)
    base = "http://%s:%s" % (HOST, PORT)
    for path in ["/", "/about", "/missing", "/index"]:
        try:
            urllib.request.urlopen(base + path, timeout=1)
        except Exception:
            pass
        time.sleep(0.05)
    time.sleep(0.1)


if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    client_requests()
