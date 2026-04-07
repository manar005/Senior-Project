"""
Generate static/pcaps/challenge_38.pcapng for Challenge 38 (ICMP payload exfil).

Requires: pip install scapy

The flag is split across several ICMP Echo Request payloads (plus decoy traffic).
Run from project root: python scripts/forensics_challenge38_icmp_exfil.py
"""

import os
import sys

try:
    from scapy.all import ICMP, IP, Raw, wrpcap
except ImportError:
    print("Install scapy: pip install scapy", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PROJECT_ROOT, "static", "pcaps", "challenge_38.pcapng")

# Submission flag (concatenate payload parts in time order)
FLAG = "ICMP_EXFIL_38"
CHUNKS = ["ICMP_", "EXFIL_", "38"]

BASE_EPOCH = 1_700_000_000.0  # stable ordering for packet times


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pkts = []
    t = BASE_EPOCH

    def icmp_echo(payload: bytes):
        nonlocal t
        p = IP(src="127.0.0.1", dst="127.0.0.1") / ICMP(type=8, code=0) / Raw(load=payload)
        p.time = t
        t += 0.001
        return p

    # Decoy ICMP traffic
    pkts.append(icmp_echo(b"NOISE_A"))
    pkts.append(icmp_echo(b"NOISE_B"))

    for chunk in CHUNKS:
        pkts.append(icmp_echo(chunk.encode("ascii")))

    pkts.append(icmp_echo(b"NOISE_C"))

    wrpcap(OUT, pkts)
    print(f"Wrote {OUT}")
    print(f"Flag (for challenge metadata): {FLAG}")


if __name__ == "__main__":
    main()
