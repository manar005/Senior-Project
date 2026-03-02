"""One-off script for Challenge 13 pcap.
Serves GET and POST: client sends GET / and GET /page then POST /submit.
Only the POST /submit response contains the flag, Base64-encoded (X-Flag + body).
Solver follows TCP stream, finds the encoded value, decodes it, submits METHOD_POST.

Run while capturing on loopback in Wireshark; save as static/pcaps/challenge_13.pcapng.
"""
import base64
import http.server
import socketserver
import threading
import time
import urllib.request

HOST = "127.0.0.1"
PORT = 8777  # Avoid conflict with 8776 (ch12) and 8765 (ch01)
FLAG = "METHOD_POST"
FLAG_ENCODED = base64.b64encode(FLAG.encode("utf-8")).decode("ascii")


class MethodHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK\n")

    def do_POST(self):
        if self.path == "/submit":
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("X-Flag", FLAG_ENCODED)
            self.end_headers()
            self.wfile.write(("Flag: %s\n" % FLAG_ENCODED).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def run_server():
    with socketserver.TCPServer((HOST, PORT), MethodHandler) as httpd:
        httpd.serve_forever()


def client_requests():
    time.sleep(0.3)
    base = "http://%s:%s" % (HOST, PORT)
    try:
        urllib.request.urlopen(base + "/", timeout=1)
    except Exception:
        pass
    time.sleep(0.05)
    try:
        urllib.request.urlopen(base + "/page", timeout=1)
    except Exception:
        pass
    time.sleep(0.05)
    try:
        req = urllib.request.Request(base + "/submit", data=b"data=hello", method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass
    time.sleep(0.1)


if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    client_requests()
