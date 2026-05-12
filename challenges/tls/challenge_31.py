"""
Challenge 31: HTTP over TLS (decrypt then read HTTP)
Category: TLS
"""
challenge = {
    'title': 'HTTP over TLS',
    'description': 'Traffic was captured while a client talked to a small HTTPS-style server on localhost. Decrypt the TLS session using the server key, then treat the decrypted bytes as HTTP: the flag appears as an HTTP response header (not as arbitrary binary application data).',
    'hint': 'Download the private key using the "Download private key" link on this page. In Wireshark: Edit → Preferences → Protocols → TLS → RSA keys list → Add: IP 127.0.0.1, Port 9443, Protocol http, Key file (your downloaded .pem). Reload or re-open the pcap. Expand the decrypted HTTP objects or inspect the TLS application data for an HTTP/1.1 response and read the custom header that carries the flag.',
    'flag': 'HTTP_TLS_FLAG',
    'expected_outcome': 'Decrypt TLS with the server RSA key, then interpret application data as HTTP and extract the flag from an HTTP response header.',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 7,
    'order_in_category': 1,
}
