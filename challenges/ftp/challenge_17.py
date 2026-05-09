"""
Challenge 17: FTP CWD Path – Base64 + Reversed (control only)
Category: FTP
"""
challenge = {
    'title': 'FTP CWD Path',
    'description': 'An FTP session was captured on port 2121. After logging in, the client changed to a directory using CWD. But the flag is not as it seems..',
    'hint': 'Filter by "tcp.port == 2121" and follow the TCP stream. Find the CWD command and its argument. Decode that argument from Base64 and reverse it to get the flag.',
    'flag': 'FTP_REVERSED',
    'expected_outcome': 'Extract the CWD argument, decode Base64, reverse the string, and submit the flag',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 4,
    'order_in_category': 2,
}
