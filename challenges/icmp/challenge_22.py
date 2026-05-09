"""
Challenge 22: ICMP Type and Code
Category: ICMP
"""
challenge = {
    'title': 'ICMP Type and Code',
    'description': 'In this capture, one ICMP packet is a "Destination Unreachable" message. The flag is ICMP_T_C where T is the ICMP type (decimal) and C is the ICMP code (decimal). Find the Type and Code in the capture and submit in that format.',
    'hint': 'Filter for ICMP with "icmp". In the ICMP header you will see Type and Code. Destination Unreachable is type 3; the code indicates the reason (e.g. 0=Net Unreachable, 1=Host Unreachable). Submit as ICMP_T_C with no spaces.',
    'flag': 'ICMP_3_1',
    'expected_outcome': 'Learn to read both ICMP type and code fields and interpret Destination Unreachable messages',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 5,
    'order_in_category': 2,
}
