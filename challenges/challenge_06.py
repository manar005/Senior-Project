"""
Challenge 6: Network Protocol Identification
"""
challenge = {
    'title': 'Network Protocol Identification',
    'description': 'Identify the application layer protocol used in this communication. The traffic you need uses port 2525. The flag is the protocol name in uppercase (e.g., SMTP, POP3, IMAP, SNMP).',
    'hint': 'Filter by "tcp.port == 2525" to see the traffic. Look at the payload (Follow → TCP Stream): you will see the protocol name. Submit it as the flag.',
    'flag': 'SMTP',
    'expected_outcome': 'Learn to identify different network protocols from packet analysis',
    'challenge_type': 'network',
    'order_num': 6
}
