"""
Challenge 24: FTP File Download (RETR)
Category: FTP
Level 4: Same flow as Challenge 23; file contains three candidate flags—only one is accepted.
"""
challenge = {
    'title': 'FTP File Download (RETR)',
    'description': 'In this capture, an FTP client downloads a file using RETR over a passive data connection (PASV). The data port is given by the formula e*128+f (from the 227 reply). Calculate to find the data port containing the flag, but some flags lie..',
    'hint': 'Filter by tcp.port == 2121. Find the PASV reply, compute the data port (e*128+f), then follow that TCP stream. The payload has three flag-like lines. Which one is the correct flag?',
    'flag': 'RETR_FILE_FLAG',
    'expected_outcome': 'Trace RETR to its data connection, extract file content, and verify which of the three candidates is the correct flag',
    'challenge_type': 'network',
    'points': 150,
    'category_id': 4,
    'order_in_category': 5,
}
