"""
Challenge 35: TLS
Category: TLS
"""
challenge = {
    'title': 'TLS Application Data',
    'description': 'After the TLS handshake, encrypted application data is exchanged. If you have the private key, decrypt the session and find the secret message. The flag is that message.',
    'hint': 'Download the private key from this page. In Wireshark: Edit → Preferences → Protocols → TLS → RSA keys list → Add: IP 127.0.0.1, Port 9444, Protocol http, Key file (your downloaded .pem). Reload the pcap. Follow the TLS stream or inspect decrypted application data; the secret message is the flag.',
    'flag': 'TLS_APP_FLAG',
    'expected_outcome': 'Decrypt TLS application data and extract the secret message',
    'challenge_type': 'network',
    'points': 150,
    'category_id': 7,
    'order_in_category': 5,
}
