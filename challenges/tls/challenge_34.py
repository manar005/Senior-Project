"""
Challenge 34: TLS
Category: TLS
"""
challenge = {
    'title': 'TLS Certificate',
    'description': 'The TLS server presents a certificate. Extract the Common Name (CN) from the server certificate and submit it as the flag.',
    'hint': 'Filter for TLS. Expand the Server Hello → Certificate. Look at the certificate chain; the first certificate has a Subject with CN=.... Submit the CN value as the flag.',
    'flag': 'CN_SERVER',
    'expected_outcome': 'Extract the server certificate Common Name from TLS handshake',
    'challenge_type': 'network',
    'points': 130,
    'category_id': 7,
    'order_in_category': 4,
}
