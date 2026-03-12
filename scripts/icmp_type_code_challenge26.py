"""
One-off script for Challenge 26 pcap. Sends one ICMP Destination Unreachable
(type=3, code=1 = Host Unreachable) so the capture contains that type/code.

Requires: pip install scapy. On macOS/Linux, run with sudo (raw sockets).
Run while capturing on loopback; save as static/pcaps/challenge_26.pcapng.
"""
import sys
import time

try:
    from scapy.all import IP, ICMP, send
except ImportError:
    print("Install scapy: pip install scapy", file=sys.stderr)
    sys.exit(1)

# One packet: ICMP Type 3 (Dest Unreachable), Code 1 (Host Unreachable)
# Send to 127.0.0.1 so it appears on loopback capture
TARGET = "127.0.0.1"

def main():
    pkt = IP(dst=TARGET) / ICMP(type=3, code=1)
    send(pkt, verbose=0)
    time.sleep(0.2)

if __name__ == "__main__":
    main()
