"""
One-off HTTP server for creating Challenge 1 pcap.
Sends the flag in response header FLAG.
Run this, then capture with Wireshark on loopback and request http://127.0.0.1:8765/
"""
import http.server
import socketserver

PORT = 8765
FLAG = "NETWORK_HTTP_FLAG"


class FlagHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("FLAG", FLAG)  # Flag in response header for Wireshark challenge
        self.end_headers()
        self.wfile.write(b"Nothing to see here. Check the response headers.\n")

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), FlagHandler) as httpd:
        print(f"Flag server for Challenge 1 pcap: http://127.0.0.1:{PORT}/")
        print("Capture this with Wireshark on loopback, then curl or open in browser.")
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()
