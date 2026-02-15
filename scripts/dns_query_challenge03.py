"""
One-off script for creating Challenge 3 pcap.
Performs a DNS query for dns.query.flag so you can capture it in Wireshark.
Run this while capturing; the DNS query will appear even if the name doesn't resolve.
"""
import socket

DOMAIN = "dns.query.flag"  # Flag will be DNS_QUERY_FLAG

if __name__ == "__main__":
    print(f"Sending DNS query for: {DOMAIN}")
    try:
        socket.getaddrinfo(DOMAIN, 80)
    except socket.gaierror:
        pass  # Expected if domain doesn't exist; the query still goes on the wire
    print("Done. Check Wireshark for the DNS query packet.")
