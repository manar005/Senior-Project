"""
Challenge 25: ICMP Type Message
Category: ICMP
"""
challenge = {
    'title': 'ICMP Type Message',
    'description': 'A host sent a sequence of ICMP packets. Each packet has its ICMP type set to a value that encodes a character (type = ASCII code). The types were sent in time order. Treat each type value as an ASCII character, concatenate in packet order, and submit that string as the flag (uppercase, no spaces).',
    'hint': 'Filter for "icmp". Sort or follow packets by time. For each ICMP packet in order, read the Type field from the ICMP header. Convert each type number to its ASCII character (decimal: 65=A, 66=B, ...). The concatenated word is the flag.',
    'flag': 'ICMP_MSG',
    'expected_outcome': 'Combine filtering, packet order, and ASCII decoding to recover a message hidden in ICMP type fields',
    'challenge_type': 'network',
    'points': 150,
    'category_id': 5,
    'order_in_category': 5,
}
