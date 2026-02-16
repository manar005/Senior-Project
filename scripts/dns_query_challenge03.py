"""One-off script for Challenge 3 pcap. Domain is FLAG.<base64> so "FLAG" is plain text; the next label is the encoded flag.
   User sees FLAG.<encoded>, decodes the encoded part → dns.query.flag, then replaces dots with underscores and uppercases → DNS_QUERY_FLAG."""
import base64
import socket

# First label is literal "FLAG" (not encoded). Second label is base64 of "dns.query.flag".
ENCODED_FLAG = base64.b64encode(b"dns.query.flag").decode().rstrip("=")
DOMAIN = f"FLAG.{ENCODED_FLAG}.local"

if __name__ == "__main__":
    try:
        socket.getaddrinfo(DOMAIN, 80)
    except socket.gaierror:
        pass
