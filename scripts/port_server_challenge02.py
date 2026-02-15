"""
One-off server for creating Challenge 2 pcap.
Listens on TCP port 8080 so the capture shows destination port 8080 (flag: PORT_0x1F90).
Run this, then capture with Wireshark on loopback and connect to http://127.0.0.1:8080/
"""
import http.server
import socketserver

PORT = 8080  # Destination port in pcap = 8080 -> hex 0x1F90 -> flag PORT_0x1F90


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"TCP connection to port 8080.\n")

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Server for Challenge 2 pcap: http://127.0.0.1:{PORT}/")
        print("Capture this with Wireshark on loopback, then curl or open in browser.")
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()
