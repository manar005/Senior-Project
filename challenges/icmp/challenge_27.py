"""
Challenge 27: ICMP Echo Identifier and Sequence
Category: ICMP

Find the identifier or sequence number in an ICMP Echo Request/Reply.
"""
challenge = {
    'title': 'ICMP Echo Identifier and Sequence',
    'description': 'This capture contains ICMP Echo Request and Echo Reply packets (ping). The flag is in the ICMP header: use the 16-bit Identifier value of the first Echo Reply packet. Submit the flag as ID_X where X is that identifier in decimal.',
    'hint': 'Filter for "icmp". Echo Reply has type 0. In the ICMP header, after Type, Code, and Checksum, there are Identifier and Sequence number fields. Use the Identifier (first 16-bit value in the payload section of the ICMP header) from the first Echo Reply.',
    'flag': 'ID_2048',
    'expected_outcome': 'Learn the structure of ICMP Echo messages and locate Identifier and Sequence fields',
    'challenge_type': 'network',
    'order_num': 27,
    'points': 120,
    'category_slug': 'icmp',
    'order_in_category': 3,
}
