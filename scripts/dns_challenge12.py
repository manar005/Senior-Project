"""
One-off script for Challenge 18 pcap. Runs a minimal DNS server on 127.0.0.1:5300
that responds to any query with a TXT record containing the flag. A client query
is sent so the capture contains both query and response. No external deps.

Usage:
  1. Start Wireshark capture on loopback (e.g. lo0).
  2. Run: python3 scripts/dns_challenge12.py
  3. Stop capture and save as static/pcaps/challenge_18.pcapng
"""
import socket
import struct
import sys
import threading
import time

# Must match challenges/dns/challenge_18.py
FLAG = "FLAG_DNS_RESPONSE"
SERVER = "127.0.0.1"
PORT = 5300


def encode_domain(name):
    """Encode domain (e.g. 'flag.local') as DNS label sequence ending with 0."""
    parts = name.split(".") if isinstance(name, str) else name
    return b"".join(bytes([len(p)]) + p.encode("ascii") for p in parts) + b"\x00"


def parse_dns_query(data):
    """Extract transaction ID and query name from a DNS request. Returns (id, qname_bytes_end)."""
    if len(data) < 12:
        return None, 0
    tid = struct.unpack("!H", data[0:2])[0]
    # Skip header (12), then read labels until 0
    pos = 12
    while pos < len(data) and data[pos] != 0:
        label_len = data[pos]
        pos += 1 + label_len
    if pos < len(data):
        pos += 1  # skip final 0
    qname = data[12:pos]  # question name
    return tid, qname, pos


def build_txt_response(trans_id, qname_bytes, query_tail_len):
    """Build a DNS response with one TXT answer. query_tail_len = len(qtype) + len(qclass) = 4."""
    # Header: ID, flags (0x8180 = response + authoritative), 1 question, 1 answer, 0, 0
    header = struct.pack("!HHHHHH", trans_id, 0x8180, 1, 1, 0, 0)
    # Question section (echo back): qname + type TXT (16) + class IN (1)
    question = qname_bytes + struct.pack("!HH", 16, 1)
    # Answer: name pointer to 0x0c (start of question), type TXT, class IN, TTL, rdlength, rdata
    txt_rdata = bytes([len(FLAG)]) + FLAG.encode("ascii")
    rdlength = len(txt_rdata)
    answer = b"\xc0\x0c" + struct.pack("!HHIH", 16, 1, 60, rdlength) + txt_rdata
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
        # Question is qname + 2 bytes type + 2 bytes class
        reply = build_txt_response(tid, data[12:q_end], 4)
        sock.sendto(reply, addr)
    finally:
        sock.close()


def run_client():
    time.sleep(0.5)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        # Minimal DNS query: id=1, flags=0, 1 question, 0 answer, 0, 0; qname flag.local; type TXT; class IN
        qname = encode_domain("flag.local")
        query = struct.pack("!HHHHHH", 1, 0x0100, 1, 0, 0, 0) + qname + struct.pack("!HH", 16, 1)
        sock.sendto(query, (SERVER, PORT))
        _ = sock.recvfrom(1024)
        print("Response received (check Wireshark).")
        sock.close()
    except Exception as e:
        print(f"Client: {e}", file=sys.stderr)


if __name__ == "__main__":
    print(f"DNS server on {SERVER}:{PORT}. Capture in Wireshark, then run this script.")
    print("Save as static/pcaps/challenge_18.pcapng")
    t = threading.Thread(target=run_client)
    t.daemon = True
    t.start()
    run_server()
    print("Done.")
