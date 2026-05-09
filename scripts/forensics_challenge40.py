"""
Generate static/pcaps/challenge_40.pcapng — DNS + HTTP two-part flag.

Requires: pip install scapy

Part A: first label of DNS query FORENSICS.reconstruct.local -> FORENSICS
Part B: HTTP 200 response body starts with _MULTI (optional second line verify=len:15)

Flag: FORENSICS + _MULTI = FORENSICS_MULTI

Decoys: extra DNS query, misleading HTTP host.

Run: python scripts/forensics_challenge40.py
"""

import os
import sys

try:
    from scapy.all import DNS, DNSQR, IP, Raw, TCP, UDP, wrpcap
except ImportError:
    print("Install scapy: pip install scapy", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PROJECT_ROOT, "static", "pcaps", "challenge_40.pcapng")

FLAG = "FORENSICS_MULTI"
HTTP_BODY = b"_MULTI\nverify=len:15\n"
DNS_QNAME = "FORENSICS.reconstruct.local"
FLAG_LEN = len(FLAG)

BASE_EPOCH = 1_711_000_000.0
HTTP_TIME = BASE_EPOCH + 4.0


def dns_query(qname: str, txid: int, t: float):
    p = (
        IP(src="127.0.0.1", dst="127.0.0.1")
        / UDP(sport=50000 + (txid % 4000), dport=53)
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


def tcp_http_exchange(sport: int, dport: int, host: bytes, path: bytes, resp_body: bytes, t0: float):
    """TCP handshake + HTTP GET + 200 + client ACK."""
    cseq, sseq = 10_000 + sport % 500, 20_000 + sport % 500
    pkts = []
    t = t0

    def stamp(p):
        nonlocal t
        p.time = t
        t += 0.0004
        return p

    pkts.append(stamp(IP(src="127.0.0.1", dst="127.0.0.1") / TCP(sport=sport, dport=dport, flags="S", seq=cseq)))
    pkts.append(
        stamp(
            IP(src="127.0.0.1", dst="127.0.0.1")
            / TCP(sport=dport, dport=sport, flags="SA", seq=sseq, ack=cseq + 1)
        )
    )
    pkts.append(
        stamp(
            IP(src="127.0.0.1", dst="127.0.0.1")
            / TCP(sport=sport, dport=dport, flags="A", seq=cseq + 1, ack=sseq + 1)
        )
    )

    req = b"GET " + path + b" HTTP/1.1\r\nHost: " + host + b"\r\n\r\n"
    pkts.append(
        stamp(
            IP(src="127.0.0.1", dst="127.0.0.1")
            / TCP(sport=sport, dport=dport, flags="PA", seq=cseq + 1, ack=sseq + 1)
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
            / TCP(sport=dport, dport=sport, flags="PA", seq=sseq + 1, ack=cseq + 1 + len(req))
            / Raw(load=resp)
        )
    )
    pkts.append(
        stamp(
            IP(src="127.0.0.1", dst="127.0.0.1")
            / TCP(
                sport=sport,
                dport=dport,
                flags="A",
                seq=cseq + 1 + len(req),
                ack=sseq + 1 + len(resp),
            )
        )
    )
    return pkts


def main():
    assert FLAG_LEN == 15
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    all_pkts = []

    all_pkts.append(dns_query("noise.placeholder.net", 0x1001, BASE_EPOCH + 0.2))
    all_pkts.append(dns_query(DNS_QNAME, 0xCAFE, BASE_EPOCH + 1.0))

    all_pkts.extend(
        tcp_http_exchange(
            49150,
            8088,
            b"wrong.local",
            b"/",
            b"token=FAKE_SUFFIX\n",
            BASE_EPOCH + 2.5,
        )
    )

    all_pkts.extend(
        tcp_http_exchange(
            49160,
            8088,
            b"capstone.local",
            b"/flag",
            HTTP_BODY,
            HTTP_TIME,
        )
    )

    all_pkts.sort(key=lambda p: p.time)
    wrpcap(OUT, all_pkts)
    print(f"Wrote {OUT}")
    print(f"Flag (for challenge metadata): {FLAG}")


if __name__ == "__main__":
    main()
