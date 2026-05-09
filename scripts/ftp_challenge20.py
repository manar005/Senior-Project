"""
Challenge 25 pcap: FTP Rename (RNFR/RNTO). All RNTO arguments are Base64-encoded; one decodes to the flag.
Save as static/pcaps/challenge_18.pcapng.
"""
import base64
import socket
import threading
import time
from ftplib import FTP

FLAG = "ANON_HIDDEN_FLAG"
DECOY1 = "DECOY_RENAME_ONE"
DECOY2 = "DECOY_RENAME_TWO"
PORT = 2121
HOST = "127.0.0.1"


def run_ftp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    try:
        conn, _ = sock.accept()
        conn.sendall(b"220 FTP Server ready\r\n")
        while True:
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
                elif upper.startswith("RNFR"):
                    conn.sendall(b"350 File exists, send RNTO\r\n")
                elif upper.startswith("RNTO"):
                    conn.sendall(b"250 Rename successful\r\n")
                elif upper.startswith("QUIT"):
                    conn.sendall(b"221 Bye\r\n")
                    conn.close()
                    return
                else:
                    conn.sendall(b"200 OK\r\n")
        conn.close()
    finally:
        sock.close()


def main():
    server_thread = threading.Thread(target=run_ftp_server, daemon=True)
    server_thread.start()
    time.sleep(0.4)
    try:
        ftp = FTP()
        ftp.connect(HOST, PORT, timeout=3)
        ftp.login("user", "pass")
        ftp.rename("decoy1.txt", base64.b64encode(DECOY1.encode()).decode())
        ftp.rename("decoy2.txt", base64.b64encode(DECOY2.encode()).decode())
        ftp.rename("secret.txt", base64.b64encode(FLAG.encode()).decode())
        ftp.quit()
    except Exception as e:
        print("Client:", e)
    time.sleep(0.3)
    print("Capture complete. Save as static/pcaps/challenge_18.pcapng")


if __name__ == "__main__":
    main()
