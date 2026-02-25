"""
Challenge 8: TCP Fragmentation
"""
challenge = {
    'title': 'TCP Fragmentation',
    'description': 'The flag was sent in fragments across multiple TCP connections on port 8888. Each connection carries one fragment. Concatenate the fragments in order to recover the full flag, then submit it.',
    'hint': 'Filter by "tcp.port == 8888". You will see several TCP connections. Click on packets with length>0 and see the fragments in the payload. Another way is to right click a packet → Follow → TCP Stream: each stream shows only one fragment. Open each stream in order (tcp.stream eq 0, then 1, then 2, then 3) and concatenate to get the flag.',
    'flag': 'REASSEMBLE_ME',
    'expected_outcome': 'Learn how data can be split across TCP segments and how to reassemble it',
    'challenge_type': 'network',
    'order_num': 8,
    'points': 100
}
