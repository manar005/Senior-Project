"""
Challenge 15: HTTPS/TLS Analysis
"""
challenge = {
    'title': 'HTTPS/TLS Analysis',
    'description': 'Analyze this HTTPS connection. What TLS version was used? The flag format is TLS_VERSION_X_X (e.g., TLS_VERSION_1_3).',
    'hint': 'Filter for TLS/SSL packets using "tls" or "ssl" filter. Look at the Client Hello packet. The TLS version is shown in the handshake protocol. Common versions: 1.0, 1.1, 1.2, 1.3.',
    'flag': 'TLS_VERSION_1_2',
    'expected_outcome': 'Understand TLS/SSL handshake and version identification',
    'challenge_type': 'network',
    'challenge_data': 'TLS 1.2 handshake detected',
    'order_num': 15
}
