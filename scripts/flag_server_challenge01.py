"""One-off HTTP server for Challenge 1 pcap. Sends flag in response header FLAG."""
import http.server
import socketserver

PORT = 8765
FLAG = "NETWORK_HTTP_FLAG"


class FlagHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("FLAG", FLAG)
        self.end_headers()
        self.wfile.write(b"Nothing to see here. Check the response headers.\n")


if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), FlagHandler) as httpd:
        httpd.serve_forever()
