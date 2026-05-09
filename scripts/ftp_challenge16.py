"""
One-off script for Challenge 4 pcap. Runs a minimal FTP server and a client that logs in
with plaintext credentials (USER ADMIN, PASS SECRET123). Flag = base64("ADMIN_SECRET123").

Run while capturing on loopback in Wireshark. Use display filter "tcp.port == 2121" (not "ftp";
Wireshark's ftp filter only matches port 21). Save as static/pcaps/challenge_16.pcapng.
"""
import socket
import threading
import time
from ftplib import FTP

# Must match challenge_04.py: USERNAME_PASSWORD in uppercase → ADMIN_SECRET123
FTP_USER = "ADMIN"
FTP_PASS = "SECRET123"
# Use high port so no admin/root is needed (21 often requires elevated privileges)
PORT = 2121
HOST = "127.0.0.1"


def run_ftp_server():
    """Minimal FTP server: accepts USER and PASS in plaintext and replies with standard codes."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    try:
        conn, _ = sock.accept()
        conn.sendall(b"220 Welcome to Challenge 4 FTP\r\n")
        done = False
        while not done:
            data = conn.recv(1024).decode("utf-8", errors="ignore")
            if not data:
                break
            for raw in data.split("\r\n"):
                line = raw.strip().upper()
                if not line:
                    continue
                if line.startswith("USER"):
                    conn.sendall(b"331 Password required\r\n")
                elif line.startswith("PASS"):
                    conn.sendall(b"230 Login successful\r\n")
                elif line.startswith("QUIT"):
                    conn.sendall(b"221 Bye\r\n")
                    done = True
                    break
                else:
                    conn.sendall(b"200 OK\r\n")
        conn.close()
    finally:
        sock.close()


def main():
    server_thread = threading.Thread(target=run_ftp_server, daemon=True)
    server_thread.start()
    time.sleep(0.3)
    try:
        ftp = FTP()
        ftp.connect(HOST, PORT, timeout=2)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.quit()
    except Exception:
        pass
    time.sleep(0.2)


if __name__ == "__main__":
    main()
