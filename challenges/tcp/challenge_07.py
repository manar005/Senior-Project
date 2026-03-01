"""
Challenge 7: TCP Handshake Count
Category: TCP
"""
challenge = {
    'title': 'TCP Handshake Count',
    'description': 'How many complete TCP three-way handshakes (SYN → SYN,ACK → ACK) are in this capture? The flag is HANDSHAKES_X where X is that number.',
    'hint': 'Filter for TCP. A three-way handshake is: one packet with [SYN], one with [SYN, ACK], one with [ACK]. Count how many such sequences complete in the capture.',
    'flag': 'HANDSHAKES_3',
    'expected_outcome': 'Learn to recognize TCP three-way handshakes in packet captures',
    'challenge_type': 'network',
    'order_num': 7,
    'points': 100,
    'category_slug': 'tcp',
    'order_in_category': 2,
}
