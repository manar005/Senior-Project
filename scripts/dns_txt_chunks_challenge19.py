"""
One-off script for Challenge 19 pcap. Runs a minimal DNS server on 127.0.0.1:5301
that responds with a TXT record built from multiple character-string chunks.
No external deps.

Usage:
  1. Start Wireshark capture on loopback (e.g. lo0).
  2. Run: python3 scripts/dns_txt_chunks_challenge19.py
  3. Stop capture and save as static/pcaps/challenge_19.pcapng
"""
import socket
import struct
import sys
import threading
import time

# Must match challenges/dns/challenge_19.py — flag is concatenation of CHUNKS
CHUNKS = ("CHUNKED_", "TXT_", "FLAG")
FLAG = "".join(CHUNKS)  # "CHUNKED_TXT_FLAG"
SERVER = "127.0.0.1"
PORT = 5301


def encode_domain(name):
    parts = name.split(".") if isinstance(name, str) else name
    return b"".join(bytes([len(p)]) + p.encode("ascii") for p in parts) + b"\x00"


def parse_dns_query(data):
    if len(data) < 12:
        return None, 0, 0
    tid = struct.unpack("!H", data[0:2])[0]
    pos = 12
    while pos < len(data) and data[pos] != 0:
        pos += 1 + data[pos]
    if pos < len(data):
        pos += 1
    return tid, data[12:pos], pos


def build_txt_chunks_rdata(chunks):
    """Build TXT RDATA as multiple <length><string> segments (RFC 1035)."""
    rdata = b""
    for s in chunks:
        b = s.encode("ascii")
        rdata += bytes([len(b)]) + b
    return rdata


def build_response(trans_id, qname_bytes):
    header = struct.pack("!HHHHHH", trans_id, 0x8180, 1, 1, 0, 0)
    question = qname_bytes + struct.pack("!HH", 16, 1)
    txt_rdata = build_txt_chunks_rdata(CHUNKS)
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
        reply = build_response(tid, qname_bytes)
        sock.sendto(reply, addr)
    finally:
        sock.close()


def run_client():
    time.sleep(0.5)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        qname = encode_domain("chunks.local")
        query = struct.pack("!HHHHHH", 1, 0x0100, 1, 0, 0, 0) + qname + struct.pack("!HH", 16, 1)
        sock.sendto(query, (SERVER, PORT))
        _ = sock.recvfrom(1024)
        print("Response received (check Wireshark).")
        sock.close()
    except Exception as e:
        print(f"Client: {e}", file=sys.stderr)


if __name__ == "__main__":
    print(f"DNS server on {SERVER}:{PORT}. Capture in Wireshark, then run this script.")
    print("Save as static/pcaps/challenge_19.pcapng")
    t = threading.Thread(target=run_client)
    t.daemon = True
    t.start()
    run_server()
    print("Done.")
