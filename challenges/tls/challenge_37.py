"""
Challenge 37: TLS (5/5)
Category: TLS
"""
challenge = {
    'title': 'TLS Application Data',
    'description': 'After the TLS handshake, encrypted application data is exchanged. If you have the private key, decrypt the session and find the secret message. The flag is that message.',
    'hint': 'Add the server private key in Wireshark (TLS → RSA keys list). Reload the pcap. Follow the TLS stream; the decrypted application data contains the flag.',
    'flag': 'TLS_APP_FLAG',
    'expected_outcome': 'Decrypt TLS application data and extract the secret message',
    'challenge_type': 'network',
    'order_num': 37,
    'points': 150,
    'category_slug': 'tls',
    'order_in_category': 5,
}
