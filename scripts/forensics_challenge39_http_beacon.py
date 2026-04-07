"""
Generate static/pcaps/challenge_39.pcapng for Challenge 39 (DNS staging → HTTP C2).

Requires: pip install scapy

Narrative: the implant resolves a C2 name (DNS), then talks HTTP to that host. Decoys include
HTTP-only noise, orphan DNS without matching HTTP, and DNS for unrelated names.

Session values in HTTP bodies are Base64-encoded (real flag and decoy token)—no plaintext secrets
in the pcap.

Run: python scripts/forensics_challenge39_http_beacon.py
"""

import base64
import os
import sys

try:
    from scapy.all import DNS, DNSQR, IP, Raw, TCP, UDP, wrpcap
except ImportError:
    print("Install scapy: pip install scapy", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PROJECT_ROOT, "static", "pcaps", "challenge_39.pcapng")

# Must match challenges/forensics/challenge_39.py
FLAG = "C2_BEACON"
DECOY_PLAINTEXT = "FAKE_BEACON"
REAL_HOST = "staging.c2-sim.local"
DPORT = 8090
BASE_EPOCH = 1_720_000_000.0


def dns_query(qname: str, txid: int, t: float):
    p = (
        IP(src="127.0.0.1", dst="127.0.0.1")
        / UDP(sport=50000 + (txid % 5000), dport=53)
        / DNS(
            id=txid & 0xFFFF,
            qr=0,
            opcode=0,
            rd=1,
            qd=DNSQR(qname=qname, qtype="A"),
        )
    )
    p.time = t
    return p


def tcp_get_exchange(sport: int, host: bytes, path: bytes, resp_body: bytes, t0: float):
    """One TCP handshake + HTTP GET + 200 + client ACK (loopback)."""
    cseq, sseq = 50_000 + sport % 1000, 60_000 + sport % 1000
    pkts = []
    t = t0

    def stamp(p):
        nonlocal t
        p.time = t
        t += 0.0004
        return p

    pkts.append(
        stamp(IP(src="127.0.0.1", dst="127.0.0.1") / TCP(sport=sport, dport=DPORT, flags="S", seq=cseq))
    )
    pkts.append(
        stamp(
            IP(src="127.0.0.1", dst="127.0.0.1")
            / TCP(sport=DPORT, dport=sport, flags="SA", seq=sseq, ack=cseq + 1)
        )
    )
    pkts.append(
        stamp(
            IP(src="127.0.0.1", dst="127.0.0.1")
            / TCP(sport=sport, dport=DPORT, flags="A", seq=cseq + 1, ack=sseq + 1)
        )
    )

    req = b"GET " + path + b" HTTP/1.1\r\nHost: " + host + b"\r\n\r\n"
    pkts.append(
        stamp(
            IP(src="127.0.0.1", dst="127.0.0.1")
            / TCP(sport=sport, dport=DPORT, flags="PA", seq=cseq + 1, ack=sseq + 1)
            / Raw(load=req)
        )
    )

    resp_hdr = (
        b"HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\n"
        b"Content-Length: %d\r\n\r\n" % len(resp_body)
    )
    resp = resp_hdr + resp_body
    pkts.append(
        stamp(
            IP(src="127.0.0.1", dst="127.0.0.1")
            / TCP(sport=DPORT, dport=sport, flags="PA", seq=sseq + 1, ack=cseq + 1 + len(req))
            / Raw(load=resp)
        )
    )
    pkts.append(
        stamp(
            IP(src="127.0.0.1", dst="127.0.0.1")
            / TCP(
                sport=sport,
                dport=DPORT,
                flags="A",
                seq=cseq + 1 + len(req),
                ack=sseq + 1 + len(resp),
            )
        )
    )
    return pkts


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    all_pkts = []

    # Benign
    all_pkts.extend(
        tcp_get_exchange(
            49170,
            b"www.example.local",
            b"/health",
            b"ok\n",
            BASE_EPOCH,
        )
    )

    # Decoy: DNS for a name we never HTTP to in this capture (orphan lookup)
    all_pkts.append(dns_query("updates.badcdn.local", 0x1111, BASE_EPOCH + 0.5))

    # Decoy: HTTP with Base64-only session blob — no prior DNS in pcap for this Host
    decoy_b64 = base64.b64encode(DECOY_PLAINTEXT.encode("ascii")).decode("ascii")
    all_pkts.extend(
        tcp_get_exchange(
            49180,
            b"metrics.telemetry.io",
            b"/v1/ping",
            f"status=ok&session={decoy_b64}\n".encode("ascii"),
            BASE_EPOCH + 1.5,
        )
    )

    # Decoy: orphan DNS (no matching HTTP for this query in the file)
    all_pkts.append(dns_query("collector.telemetry.net", 0x2222, BASE_EPOCH + 2.5))

    # Real chain: resolve C2 name, then HTTP to same Host header
    all_pkts.append(dns_query(REAL_HOST, 0xBEEF, BASE_EPOCH + 5.0))
    real_b64 = base64.b64encode(FLAG.encode("ascii")).decode("ascii")
    all_pkts.extend(
        tcp_get_exchange(
            49183,
            REAL_HOST.encode("ascii"),
            b"/beacon/check",
            f"session={real_b64}\n".encode("ascii"),
            BASE_EPOCH + 7.0,
        )
    )

    all_pkts.sort(key=lambda p: p.time)
    wrpcap(OUT, all_pkts)
    print(f"Wrote {OUT}")
    print(f"Flag (for challenge metadata): {FLAG}")


if __name__ == "__main__":
    main()
