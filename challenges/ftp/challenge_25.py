"""
Challenge 25: FTP Rename (RNFR/RNTO) – multiple renames; RNTO arguments are encoded; one decodes to the flag.
"""
challenge = {
    'title': 'FTP Rename (RNFR/RNTO)',
    'description': 'This capture contains FTP traffic on port 2121. The client renames files several times (RNFR/RNTO). One of the RNTO arguments is the flag.',
    'hint': 'Filter by tcp.port == 2121. Follow the TCP stream and find all RNTO commands. Each argument is encoded (Base64). Decode each argument; the flag is one of the decoded strings.',
    'flag': 'ANON_HIDDEN_FLAG',
    'expected_outcome': 'Find multiple RNTO arguments, decode each, and submit the one that is the flag',
    'challenge_type': 'network',
    'order_num': 25,
    'points': 100,
    'category_slug': 'ftp',
    'order_in_category': 3,
}
