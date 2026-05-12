"""
Challenge 23 pcap: FTP Passive Mode Data Connection.
Server on 2121 (control); client uses PASV then LIST. Flag is in the data stream (LIST payload).

Run while capturing on loopback in Wireshark. Filter "tcp.port == 2121" for control;
find 227 reply for data port (e*256+f), then follow that TCP stream for the flag.
Save as static/pcaps/challenge_18.pcapng.
"""
import socket
import threading
import time
from ftplib import FTP

FLAG = "PASV_DATA_FLAG"
PORT = 2121
HOST = "127.0.0.1"


def run_ftp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    data_sock = None
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
                elif upper.startswith("PASV"):
                    if data_sock:
                        try:
                            data_sock.close()
                        except Exception:
                            pass
                    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    data_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    data_sock.bind((HOST, 0))
                    data_sock.listen(1)
                    p = data_sock.getsockname()[1]
                    e, f = p // 256, p % 256
                    conn.sendall(
                        f"227 Entering Passive Mode (127,0,0,1,{e},{f})\r\n".encode("utf-8")
                    )
                elif upper.startswith("LIST") or upper == "LIST":
                    conn.sendall(b"150 Opening data connection\r\n")
                    if data_sock:
                        try:
                            data_conn, _ = data_sock.accept()
                            listing = f"file1.txt\r\nreadme.txt\r\n{FLAG}\r\nnotes.txt\r\n"
                            data_conn.sendall(listing.encode("utf-8"))
                            data_conn.close()
                        except Exception:
                            pass
                    conn.sendall(b"226 Transfer complete\r\n")
                elif upper.startswith("QUIT"):
                    conn.sendall(b"221 Bye\r\n")
                    if data_sock:
                        try:
                            data_sock.close()
                        except Exception:
                            pass
                    conn.close()
                    return
                else:
                    conn.sendall(b"200 OK\r\n")
        if data_sock:
            try:
                data_sock.close()
            except Exception:
                pass
        conn.close()
    finally:
        sock.close()
        if data_sock:
            try:
                data_sock.close()
            except Exception:
                pass


def main():
    server_thread = threading.Thread(target=run_ftp_server, daemon=True)
    server_thread.start()
    time.sleep(0.4)
    try:
        ftp = FTP()
        ftp.connect(HOST, PORT, timeout=3)
        ftp.login("user", "pass")
        ftp.retrlines("LIST")
        ftp.quit()
    except Exception as e:
        print("Client:", e)
    time.sleep(0.3)
    print("Capture complete. Save as static/pcaps/challenge_18.pcapng")


if __name__ == "__main__":
    main()
