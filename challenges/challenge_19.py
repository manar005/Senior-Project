"""
Challenge 19: Network Protocol Identification
"""
challenge = {
    'title': 'Network Protocol Identification',
    'description': 'Identify the application layer protocol used in this communication. The flag is PROTOCOL_NAME in uppercase (e.g., SMTP, POP3, IMAP, SNMP).',
    'hint': 'Look at the application layer data in the packets. Check the port numbers and payload. Common protocols: SMTP (25), POP3 (110), IMAP (143), SNMP (161), Telnet (23).',
    'flag': 'SMTP',
    'expected_outcome': 'Learn to identify different network protocols from packet analysis',
    'challenge_type': 'network',
    'challenge_data': 'SMTP protocol on port 25',
    'order_num': 19
}
