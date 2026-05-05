"""
Challenge 28: Multiple ICMP Types
Category: ICMP

A capture contains several different ICMP message types; identify the one that appears a given number of times.
"""
challenge = {
    'title': 'Multiple ICMP Types',
    'description': 'This capture contains a mix of ICMP packet types: Echo Request (8), Echo Reply (0), Time Exceeded (11), and Destination Unreachable (3). One of these types appears exactly three times. The flag is the word TYPE followed by that type number (e.g. TYPE8 or TYPE3—find which one appears three times).',
    'hint': 'Use Statistics → Conversations or a filter like "icmp" and count packets by type. In Wireshark, expand each ICMP packet and note the "Type" field. Count how many packets have type 0, 8, 3, and 11. The type that appears exactly 3 times gives you the flag (TYPE followed by that number).',
    'flag': 'TYPE11',
    'expected_outcome': 'Learn to filter and count ICMP packets by type across a mixed capture',
    'challenge_type': 'network',
    'points': 130,
    'category_id': 5,
    'order_in_category': 4,
}
