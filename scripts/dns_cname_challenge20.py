"""
One-off script for Challenge 20 pcap. Runs a minimal DNS server on 127.0.0.1:5302
that responds with a CNAME record. The CNAME target is "flag.via.cname" so the
flag (after dots→underscores, uppercase) is FLAG_VIA_CNAME. No external deps.

Usage:
  1. Start Wireshark capture on loopback (e.g. lo0).
  2. Run: python3 scripts/dns_cname_challenge20.py
  3. Stop capture and save as static/pcaps/challenge_20.pcapng
"""
import socket
import struct
import sys
import threading
import time

# Must match challenges/dns/challenge_20.py — flag = CNAME target with .→_ and upper
CNAME_TARGET = "flag.via.cname"  # → FLAG_VIA_CNAME
SERVER = "127.0.0.1"
PORT = 5302


def encode_domain(name):
    parts = name.split(".") if isinstance(name, str) else name
    return b"".join(bytes([len(p)]) + p.encode("ascii") for p in parts) + b"\x00"


def parse_dns_query(data):
    if len(data) < 12:
        return None, None, 0
    tid = struct.unpack("!H", data[0:2])[0]
    pos = 12
    while pos < len(data) and data[pos] != 0:
        pos += 1 + data[pos]
    if pos < len(data):
        pos += 1
    return tid, data[12:pos], pos


def build_response(trans_id, qname_bytes):
    # Header: ID, flags, 1 question, 1 answer
    header = struct.pack("!HHHHHH", trans_id, 0x8180, 1, 1, 0, 0)
    # Question: qname + type CNAME (5) + class IN (1)
    question = qname_bytes + struct.pack("!HH", 5, 1)
    # Answer: name pointer 0xc00c, type CNAME (5), class IN, TTL, rdlength, rdata (encoded CNAME target)
    cname_rdata = encode_domain(CNAME_TARGET)
    rdlength = len(cname_rdata)
    answer = b"\xc0\x0c" + struct.pack("!HHIH", 5, 1, 60, rdlength) + cname_rdata
    return header + question + answer


def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SERVER, PORT))
    try:
        data, addr = sock.recvfrom(1024)
        tid, qname_bytes, q_end = parse_dns_query(data)
        if tid is None:
            return
        reply = build_response(tid, qname_bytes)
        sock.sendto(reply, addr)
    finally:
        sock.close()


def run_client():
    time.sleep(0.5)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        qname = encode_domain("cname.local")
        # Query type CNAME (5)
        query = struct.pack("!HHHHHH", 1, 0x0100, 1, 0, 0, 0) + qname + struct.pack("!HH", 5, 1)
        sock.sendto(query, (SERVER, PORT))
        _ = sock.recvfrom(1024)
        print("Response received (check Wireshark).")
        sock.close()
    except Exception as e:
        print(f"Client: {e}", file=sys.stderr)


if __name__ == "__main__":
    print(f"DNS server on {SERVER}:{PORT}. Capture in Wireshark, then run this script.")
    print("Save as static/pcaps/challenge_20.pcapng")
    t = threading.Thread(target=run_client)
    t.daemon = True
    t.start()
    run_server()
    print("Done.")
