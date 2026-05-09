"""
Challenge 27: SMTP Command Sequence
Category: SMTP
"""
challenge = {
    'title': 'SMTP Command Sequence',
    'description': 'In this capture, an SMTP client sends a sequence of commands to the server. Identify the second command sent. The flag is that command in uppercase, with spaces replaced by underscores.',
    'hint': 'Filter by tcp.port == 2525 (or the SMTP port in the capture). Follow the TCP stream and read the client commands in order. The first is usually EHLO/HELO; the second command is the flag format.',
    'flag': 'MAIL_FROM:<SENDER@CHALLENGE.LAB>',
    'expected_outcome': 'Learn SMTP command order and extract a specific command from the stream',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 6,
    'order_in_category': 2,
}
