"""
Challenge 16: FTP Credential Extraction (submit encoded flag)
Category: FTP
"""
import base64

_FLAG_PLAINTEXT = 'ADMIN_SECRET123'
challenge = {
    'title': 'FTP Credential Extraction',
    'description': 'An FTP login was captured in this traffic. The packets you need use port 2121. Find the username and password, then format them as USERNAME_PASSWORD in uppercase. Encode that string (Base64) and submit the encoded value as the flag.',
    'hint': 'Filter by "tcp.port == 2121". Click one of those packets, then right click any packet in that connection → Follow → TCP Stream to see the full login (USER ... and PASS ...) in one window. Combine as USERNAME_PASSWORD, encode (Base64), and submit.',
    'flag': base64.b64encode(_FLAG_PLAINTEXT.encode()).decode(),
    'expected_outcome': 'Understand FTP protocol security issues and credential extraction',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 4,
    'order_in_category': 1,
}
