"""
One-off script for Challenge 29 pcap. Sends a sequence of ICMP packets
whose Type field values are ASCII codes for "ICMP_MSG":
  I=73, C=67, M=77, P=80, _=95, M=77, S=83, G=71.

Requires: pip install scapy. On macOS/Linux, run with sudo (raw sockets).
Run while capturing on loopback; save as static/pcaps/challenge_25.pcapng.
"""
import sys
import time

try:
    from scapy.all import IP, ICMP, send
except ImportError:
    print("Install scapy: pip install scapy", file=sys.stderr)
    sys.exit(1)

TARGET = "127.0.0.1"
# ICMP_MSG as ASCII decimal: 73, 67, 77, 80, 95, 77, 83, 71
FLAG_TYPES = [ord(c) for c in "ICMP_MSG"]

def main():
    for i, t in enumerate(FLAG_TYPES):
        # Use code=0; id/seq vary so packets are distinct
        pkt = IP(dst=TARGET) / ICMP(type=t, code=0, id=3000 + i, seq=1)
        send(pkt, verbose=0)
        time.sleep(0.05)
    time.sleep(0.2)

if __name__ == "__main__":
    main()
