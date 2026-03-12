"""
Challenge 35: TLS (3/5)
Category: TLS
"""
challenge = {
    'title': 'TLS Cipher Suite',
    'description': 'In the TLS Server Hello, the server selects a cipher suite. Find the hexadecimal value of the selected cipher suite (two bytes) and submit as CIPHER_XXXX (four hex characters, e.g. CIPHER_0A1B).',
    'hint': 'Filter for TLS. Expand Server Hello → Cipher Suite. The value is shown as 0xXXXX. Submit CIPHER_ followed by the four hex characters (uppercase, no 0x).',
    'flag': 'CIPHER_C02F',
    'expected_outcome': 'Identify the negotiated TLS cipher suite from Server Hello',
    'challenge_type': 'network',
    'order_num': 35,
    'points': 120,
    'category_slug': 'tls',
    'order_in_category': 3,
}
