"""
One-off script for Challenge 27 pcap. Sends one ICMP Echo Request with
Identifier=2048 to 127.0.0.1; the OS usually replies with Echo Reply
using the same Identifier. Capture shows Request and Reply with ID 2048.

Requires: pip install scapy. On macOS/Linux, run with sudo (raw sockets).
Run while capturing on loopback; save as static/pcaps/challenge_23.pcapng.
"""
import sys
import time

try:
    from scapy.all import IP, ICMP, send
except ImportError:
    print("Install scapy: pip install scapy", file=sys.stderr)
    sys.exit(1)

TARGET = "127.0.0.1"
IDENTIFIER = 2048  # Flag is ID_2048

def main():
    # Echo Request: type=8, code=0; id=2048, seq=1
    pkt = IP(dst=TARGET) / ICMP(type=8, code=0, id=IDENTIFIER, seq=1)
    send(pkt, verbose=0)
    time.sleep(0.5)  # wait for reply

if __name__ == "__main__":
    main()
