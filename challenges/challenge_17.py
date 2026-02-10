"""
Challenge 17: FTP Credential Extraction
"""
challenge = {
    'title': 'FTP Credential Extraction',
    'description': 'An FTP connection was captured. Extract the username and password from the packets. The flag format is USERNAME_PASSWORD in uppercase.',
    'hint': 'Filter for FTP traffic using "ftp" filter. FTP sends credentials in plain text. Look for USER and PASS commands in the packet details. The username and password follow these commands.',
    'flag': 'ADMIN_SECRET123',
    'expected_outcome': 'Understand FTP protocol security issues and credential extraction',
    'challenge_type': 'network',
    'challenge_data': 'FTP login: admin / secret123',
    'order_num': 17
}
