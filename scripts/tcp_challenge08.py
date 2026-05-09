"""
One-off script for Challenge 8 pcap. Sends the flag in 4 separate TCP connections:
each connection carries one fragment (REAS, SEMB, LE_M, E). So each "Follow TCP Stream"
in Wireshark shows only one fragment; solver must open each stream and concatenate in order.
Flag = REASSEMBLE_ME.

Run while capturing on loopback in Wireshark; save as static/pcaps/challenge_08.pcapng.
"""
import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 8888
CHUNKS = ["REAS", "SEMB", "LE_M", "E"]


def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(4)
    try:
        for chunk in CHUNKS:
            conn, _ = sock.accept()
            conn.sendall(chunk.encode())
            conn.close()
            time.sleep(0.03)
    finally:
        sock.close()


def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(0.3)
    for chunk in CHUNKS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((HOST, PORT))
            s.recv(1024)
            s.close()
        except (socket.timeout, socket.error, OSError):
            pass
        time.sleep(0.02)
    time.sleep(0.1)


if __name__ == "__main__":
    main()
