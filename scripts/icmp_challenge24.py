"""
One-off script for Challenge 28 pcap. Sends a mix of ICMP types so that
one type appears exactly 3 times: Time Exceeded (11) x3, Echo (8) x2,
Echo Reply (0) x2, Dest Unreachable (3) x2. Flag = TYPE11.

Requires: pip install scapy. On macOS/Linux, run with sudo (raw sockets).
Run while capturing on loopback; save as static/pcaps/challenge_24.pcapng.
"""
import sys
import time

try:
    from scapy.all import IP, ICMP, send
except ImportError:
    print("Install scapy: pip install scapy", file=sys.stderr)
    sys.exit(1)

TARGET = "127.0.0.1"

def main():
    # Type 11 (Time Exceeded) x3 -> flag TYPE11
    for _ in range(3):
        send(IP(dst=TARGET) / ICMP(type=11, code=0), verbose=0)
        time.sleep(0.05)
    # Type 8 (Echo Request) x2
    for i in range(2):
        send(IP(dst=TARGET) / ICMP(type=8, code=0, id=1000+i, seq=1), verbose=0)
        time.sleep(0.05)
    # Type 0 (Echo Reply) x2
    for i in range(2):
        send(IP(dst=TARGET) / ICMP(type=0, code=0, id=2000+i, seq=1), verbose=0)
        time.sleep(0.05)
    # Type 3 (Dest Unreachable) x2
    for _ in range(2):
        send(IP(dst=TARGET) / ICMP(type=3, code=0), verbose=0)
        time.sleep(0.05)
    time.sleep(0.2)

if __name__ == "__main__":
    main()
