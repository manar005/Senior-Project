"""
One-off script for Challenge 17 pcap. Sends TCP SYNs to ports that spell KNOCK_OPEN
(port = ASCII code: 75, 78, 79, 67, 75, 95, 79, 80, 69, 78).

Run while capturing on loopback in Wireshark; save as static/pcaps/challenge_17.pcapng.
"""
import socket
import time

HOST = "127.0.0.1"
# KNOCK_OPEN: each character's ASCII code is the destination port
PORTS = [75, 78, 79, 67, 75, 95, 79, 80, 69, 78]  # K N O C K _ O P E N


def main():
    for port in PORTS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect((HOST, port))
            s.close()
        except (socket.timeout, OSError, ConnectionRefusedError):
            pass
        time.sleep(0.05)


if __name__ == "__main__":
    main()
