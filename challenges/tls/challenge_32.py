"""
Challenge 32: TLS
Category: TLS
"""
challenge = {
    'title': 'TLS Handshake',
    'description': 'This capture contains a TLS handshake. Find the handshake Version field and read its two bytes in hex. Build the answer as TLSVER_X_Y, where X is the first byte value and Y is the second byte value.',
    'hint': 'Filter for TLS and open Client Hello or Server Hello. Under TLS Record Layer / Handshake, find the Version field. Take the two version bytes and place their numeric values into the TLSVER_X_Y format.',
    'flag': 'TLSVER_3_3',
    'expected_outcome': 'Identify TLS version from handshake packets',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 7,
    'order_in_category': 2,
}
