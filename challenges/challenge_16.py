"""
Challenge 16: ICMP Packet Analysis
"""
challenge = {
    'title': 'ICMP Packet Analysis',
    'description': 'An ICMP packet was captured. What is the ICMP type code? The flag is ICMP_TYPE_X where X is the type code number.',
    'hint': 'Filter for ICMP packets using "icmp" filter. The ICMP type is in the ICMP header. Common types: 0 (Echo Reply), 8 (Echo Request), 3 (Destination Unreachable), 11 (Time Exceeded).',
    'flag': 'ICMP_TYPE_8',
    'expected_outcome': 'Learn ICMP protocol and packet types',
    'challenge_type': 'network',
    'challenge_data': 'ICMP Echo Request (Type 8) packet',
    'order_num': 16
}
