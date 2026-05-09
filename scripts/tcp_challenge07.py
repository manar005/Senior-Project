"""
One-off script for Challenge 7 pcap. Creates 3 TCP connections (3 complete
three-way handshakes). Flag = HANDSHAKES_3.

Run while capturing on loopback in Wireshark; save as static/pcaps/challenge_07.pcapng.
"""
import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 9999
NUM_HANDSHAKES = 3


def run_server():
    """Accept NUM_HANDSHAKES connections, then close."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(NUM_HANDSHAKES)
    try:
        for _ in range(NUM_HANDSHAKES):
            conn, _ = sock.accept()
            conn.close()
    finally:
        sock.close()


def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(0.2)
    for _ in range(NUM_HANDSHAKES):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((HOST, PORT))
            s.close()
        except (socket.timeout, socket.error, OSError):
            pass
        time.sleep(0.05)
    time.sleep(0.1)


if __name__ == "__main__":
    main()
