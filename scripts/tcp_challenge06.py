"""TCP server on port 8080 for pcap suffix **06** (TCP port / handshake intro).
Run while capturing on loopback; save as **static/pcaps/challenge_06.pcapng**.

One-off server for creating Challenge 2 pcap. Listens on port 8080 (flag: PORT_1F90)."""
import http.server
import socketserver

PORT = 8080


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"TCP connection to port 8080.\n")


if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        httpd.serve_forever()
