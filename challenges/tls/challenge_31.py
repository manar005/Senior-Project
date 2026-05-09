"""
Challenge 31: TLS Decryption
Category: TLS
"""
challenge = {
    'title': 'TLS Decryption',
    'description': 'A secret message was sent over a TLS connection. The capture shows the encrypted session. Use the server\'s private key (provided in the hint) to decrypt the traffic in Wireshark and find the full message—that message is the flag.',
    'hint': 'Download the private key using the "Download private key" link on this page. In Wireshark: Edit → Preferences → Protocols → TLS → RSA keys list → Add: IP 127.0.0.1, Port 9443, Protocol http, Key file (your downloaded .pem). Reload or re-open the pcap; the TLS stream will decrypt. Follow the TLS stream or look at decrypted application data to see the flag.',
    'flag': 'TLS_DECRYPT_16',
    'expected_outcome': 'Learn how to decrypt TLS traffic in Wireshark using a server private key and locate the application data (flag).',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 7,
    'order_in_category': 2,
}
