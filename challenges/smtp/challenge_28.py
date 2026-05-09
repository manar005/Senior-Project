"""
Challenge 28: SMTP Reply Code
Category: SMTP
"""
challenge = {
    'title': 'SMTP Reply Code',
    'description': 'The SMTP server in this capture sends numeric reply codes. After the client sends DATA, the server responds with a three-digit code meaning "start mail input". The flag is REPLY_XXX where XXX is that code.',
    'hint': 'Filter for tcp.port == 2525 and follow the TCP stream. After the client sends DATA, the server replies with code 354 (start mail input). Submit REPLY_354.',
    'flag': 'REPLY_354',
    'expected_outcome': 'Identify SMTP reply codes from server responses',
    'challenge_type': 'network',
    'points': 120,
    'category_id': 6,
    'order_in_category': 3,
}
