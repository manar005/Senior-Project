"""
Challenge 24 pcap: FTP RETR; file contains three flag candidates (only RETR_FILE_FLAG is accepted).
Data port formula: e*128+f (not 256). Order in file: DECOY_FLAG_ALPHA, RETR_FILE_FLAG, DECOY_FLAG_BETA.
"""
import re
import socket
import threading
import time

FLAG = "RETR_FILE_FLAG"
FILENAME = "secret.txt"
FILE_CONTENT = "DECOY_FLAG_ALPHA\nRETR_FILE_FLAG\nDECOY_FLAG_BETA\n"

# Data port = e*128+f with e!=0. e=2, f=100 -> port 356
E, F = 2, 100
DATA_PORT = E * 128 + F  # 356

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
                    data_sock.bind((HOST, DATA_PORT))
                    data_sock.listen(1)
                    conn.sendall(
                        f"227 Entering Passive Mode (127,0,0,1,{E},{F})\r\n".encode("utf-8")
                    )
                elif upper.startswith("RETR"):
                    conn.sendall(b"150 Opening data connection\r\n")
                    if data_sock:
                        try:
                            data_conn, _ = data_sock.accept()
                            data_conn.sendall(FILE_CONTENT.encode("utf-8"))
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


def ftp_client_128():
    """Custom client: uses e*128+f for PASV data port (challenge 24 formula)."""
    ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl.settimeout(3)
    ctrl.connect((HOST, PORT))

    def recv_line():
        buf = b""
        while b"\r\n" not in buf:
            buf += ctrl.recv(1)
        return buf.decode("utf-8", errors="ignore").strip()

    recv_line()  # 220
    ctrl.sendall(b"USER user\r\n")
    recv_line()  # 331
    ctrl.sendall(b"PASS pass\r\n")
    recv_line()  # 230
    ctrl.sendall(b"PASV\r\n")
    line = recv_line()  # 227 Entering Passive Mode (127,0,0,1,e,f)
    m = re.search(r"\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)", line)
    if m:
        e, f = int(m.group(5)), int(m.group(6))
        data_port = e * 128 + f  # challenge 24 formula
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_sock.settimeout(2)
        data_sock.connect((HOST, data_port))
        ctrl.sendall(f"RETR {FILENAME}\r\n".encode("utf-8"))
        recv_line()  # 150
        chunk = data_sock.recv(4096)
        data_sock.close()
        recv_line()  # 226
    ctrl.sendall(b"QUIT\r\n")
    recv_line()
    ctrl.close()


def main():
    server_thread = threading.Thread(target=run_ftp_server, daemon=True)
    server_thread.start()
    time.sleep(0.4)
    try:
        ftp_client_128()
    except Exception as e:
        print("Client:", e)
    time.sleep(0.3)
    print("Capture complete. Save as static/pcaps/challenge_20.pcapng")


if __name__ == "__main__":
    main()
