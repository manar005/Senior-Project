"""
One-off script for Challenge 21 pcap. Runs a minimal DNS server on 127.0.0.1:5303
that responds with two answer records: first a CNAME (target "think.dns"), then a
TXT ("FINAL"). Flag = THINK_DNS + _ + FINAL = THINK_DNS_FINAL. No external deps.

Usage:
  1. Start Wireshark capture on loopback (e.g. lo0).
  2. Run: python3 scripts/dns_cname_txt_challenge21.py
  3. Stop capture and save as static/pcaps/challenge_21.pcapng
"""
import socket
import struct
import sys
import threading
import time

# Must match challenges/dns/challenge_21.py — CNAME target → THINK_DNS, TXT → FINAL
CNAME_TARGET = "think.dns"   # dots→underscores, upper = THINK_DNS
TXT_VALUE = "FINAL"           # flag = THINK_DNS_FINAL
SERVER = "127.0.0.1"
PORT = 5303


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
    # Header: 1 question, 2 answers
    header = struct.pack("!HHHHHH", trans_id, 0x8180, 1, 2, 0, 0)
    question = qname_bytes + struct.pack("!HH", 5, 1)  # type CNAME for query

    # Answer 1: CNAME — name pointer to question (0x0c), type CNAME (5), rdata = encoded target
    cname_rdata = encode_domain(CNAME_TARGET)
    ans1 = b"\xc0\x0c" + struct.pack("!HHIH", 5, 1, 60, len(cname_rdata)) + cname_rdata

    # Answer 2: TXT — same name (pointer 0x0c), type TXT (16), rdata = length + string
    txt_rdata = bytes([len(TXT_VALUE)]) + TXT_VALUE.encode("ascii")
    ans2 = b"\xc0\x0c" + struct.pack("!HHIH", 16, 1, 60, len(txt_rdata)) + txt_rdata

    return header + question + ans1 + ans2


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
        qname = encode_domain("final.local")
        query = struct.pack("!HHHHHH", 1, 0x0100, 1, 0, 0, 0) + qname + struct.pack("!HH", 5, 1)
        sock.sendto(query, (SERVER, PORT))
        _ = sock.recvfrom(1024)
        print("Response received (check Wireshark).")
        sock.close()
    except Exception as e:
        print(f"Client: {e}", file=sys.stderr)


if __name__ == "__main__":
    print(f"DNS server on {SERVER}:{PORT}. Capture in Wireshark, then run this script.")
    print("Save as static/pcaps/challenge_21.pcapng")
    t = threading.Thread(target=run_client)
    t.daemon = True
    t.start()
    run_server()
    print("Done.")
