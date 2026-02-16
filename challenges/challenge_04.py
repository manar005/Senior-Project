"""
Challenge 4: FTP Credential Extraction (submit encoded flag)
"""
import base64

# User finds plaintext credentials; they must encode USERNAME_PASSWORD (e.g. base64) and submit that
_FLAG_PLAINTEXT = 'ADMIN_SECRET123'
challenge = {
    'title': 'FTP Credential Extraction',
    'description': 'An FTP connection was captured on port 2121. Filter by "tcp.port == 2121" to see the traffic. The packets that contain the login are the ones whose payload includes "USER" and "PASS"—pick that connection and extract the username and password (plaintext). Format as USERNAME_PASSWORD in uppercase, encode (e.g. Base64), and submit the encoded form as the flag.',
    'hint': 'Filter by "tcp.port == 2121". The username and password are in packets that carry data: look for "[PSH, ACK]" in the Info column with Len > 0. Click one of those packets, then look at the bottom pane (Packet Bytes): the right-hand ASCII column shows "USER" and "PASS" with the credentials in plain text. Easier: right‑click any packet in that connection → Follow → TCP Stream to see the full login (USER ... and PASS ...) in one window. Combine as USERNAME_PASSWORD, encode (e.g. Base64), and submit.',
    'flag': base64.b64encode(_FLAG_PLAINTEXT.encode()).decode(),
    'expected_outcome': 'Understand FTP protocol security issues and credential extraction',
    'challenge_type': 'network',
    'order_num': 4
}
