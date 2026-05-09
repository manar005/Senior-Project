"""
Challenge 32: TLS
Category: TLS
"""
challenge = {
    'title': 'TLS Handshake',
    'description': 'This capture contains a TLS handshake. Identify the TLS version negotiated (e.g. TLS 1.2 or 1.3). The flag is TLSVER_X_Y where X and Y are the major and minor version from the handshake (e.g. TLSVER_3_4 means version 3.4).',
    'hint': 'Filter for TLS. In the Client Hello or Server Hello, look at the Version field. TLS 1.2 = 0x0303 (3.3), TLS 1.3 = 0x0304 (3.4). Submit TLSVER_3_3 or TLSVER_3_4.',
    'flag': 'TLSVER_3_3',
    'expected_outcome': 'Identify TLS version from handshake packets',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 7,
    'order_in_category': 1,
}
