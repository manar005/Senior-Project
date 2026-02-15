"""One-off script for Challenge 3 pcap. Sends a DNS query for dns.query.flag (flag: DNS_QUERY_FLAG)."""
import socket

DOMAIN = "dns.query.flag"

if __name__ == "__main__":
    try:
        socket.getaddrinfo(DOMAIN, 80)
    except socket.gaierror:
        pass
