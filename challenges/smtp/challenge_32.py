"""
Challenge 32: SMTP (4/5)
Category: SMTP
"""
challenge = {
    'title': 'SMTP Header Extraction',
    'description': 'An email was sent over SMTP. The message body or headers contain a secret. Find the header that holds the flag and submit the header value as the flag.',
    'hint': 'Follow the TCP stream for the SMTP data. After DATA, the client sends headers and body. Look for a custom header or a line that looks like the flag.',
    'flag': 'SMTP_HEADER_FLAG',
    'expected_outcome': 'Parse SMTP message content and extract a header or body secret',
    'challenge_type': 'network',
    'order_num': 32,
    'points': 130,
    'category_slug': 'smtp',
    'order_in_category': 4,
}
