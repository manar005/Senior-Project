"""
One-off script for Challenge (SMTP protocol ID; pcap suffix 26) pcap. Runs a minimal SMTP server and a client that
performs a short SMTP dialog (HELO, QUIT). Flag = SMTP (protocol identification).

Run while capturing on loopback in Wireshark; save as static/pcaps/challenge_26.pcapng.
Uses port 2525 so no admin/root is required (standard SMTP is port 25).
"""
import socket
import threading
import time

PORT = 2525
HOST = "127.0.0.1"


def run_smtp_server():
    """Minimal SMTP server: sends banner and responds to HELO and QUIT."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    try:
        conn, _ = sock.accept()
        conn.sendall(b"220 localhost ESMTP Challenge (SMTP protocol ID; pcap suffix 26)\r\nProtocol: SMTP\r\n")
        while True:
            data = conn.recv(1024).decode("utf-8", errors="ignore")
            if not data:
                break
            line = data.strip().upper()
            if line.startswith("HELO") or line.startswith("EHLO"):
                conn.sendall(b"250 Hello\r\n")
            elif line.startswith("QUIT"):
                conn.sendall(b"221 Bye\r\n")
                break
            else:
                conn.sendall(b"250 OK\r\n")
        conn.close()
    finally:
        sock.close()


def main():
    server_thread = threading.Thread(target=run_smtp_server, daemon=True)
    server_thread.start()
    time.sleep(0.3)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, PORT))
        s.recv(1024)
        s.sendall(b"HELO client\r\n")
        s.recv(1024)
        s.sendall(b"QUIT\r\n")
        s.recv(1024)
        s.close()
    except Exception:
        pass
    time.sleep(0.2)


if __name__ == "__main__":
    main()
