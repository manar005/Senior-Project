"""
Challenge 22 pcap: FTP CWD with Base64(reversed flag).
Client sends CWD <base64(reversed(flag))>. Solver decodes Base64 then reverses to get flag.

Run while capturing on loopback in Wireshark. Filter "tcp.port == 2121".
Save as static/pcaps/challenge_17.pcapng.
"""
import base64
import socket
import threading
import time
from ftplib import FTP

FLAG = "FTP_REVERSED"
# CWD argument = Base64( reversed(flag) ) → decode then reverse to get flag
CWD_PATH = base64.b64encode(FLAG[::-1].encode()).decode()
PORT = 2121
HOST = "127.0.0.1"


def run_ftp_server():
    """FTP server: USER, PASS, PWD → 257, CWD (any path) → 250, QUIT. No PASV/data."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    try:
        conn, _ = sock.accept()
        conn.sendall(b"220 FTP Server ready\r\n")
        done = False
        while not done:
            data = conn.recv(1024).decode("utf-8", errors="ignore")
            if not data:
                break
            for raw in data.split("\r\n"):
                line = raw.strip()
                if not line:
                    continue
                upper = line.upper()
                if upper.startswith("USER"):
                    conn.sendall(b"331 Password required\r\n")
                elif upper.startswith("PASS"):
                    conn.sendall(b"230 Login successful\r\n")
                elif upper.startswith("PWD") or upper.startswith("XPWD"):
                    conn.sendall(b'257 "/home" is current directory\r\n')
                elif upper.startswith("CWD"):
                    conn.sendall(b"250 CWD successful\r\n")
                elif upper.startswith("QUIT"):
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
        ftp.login("user", "pass")
        ftp.sendcmd("PWD")
        ftp.sendcmd(f"CWD {CWD_PATH}")  # CWD MjJfR0FMRl9QVEY= (Base64 of 22_GALF_PTF)
        ftp.quit()
    except Exception:
        pass
    time.sleep(0.2)
    print("Capture complete. Save as static/pcaps/challenge_17.pcapng")


if __name__ == "__main__":
    main()
