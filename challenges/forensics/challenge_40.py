"""
Challenge 40: Multi-Protocol Reconstruction (DNS + HTTP)
Category: Forensics
"""
challenge = {
    'title': 'Multi-Protocol Reconstruction',
    'description': 'The flag is split across DNS and HTTP on loopback, in chronological order. Part A is the first label of the queried DNS name. Part B completes the flag in the HTTP response body. Concatenate Part A + Part B to get the flag.',
    'hint': 'Filter dns for FORENSICS.reconstruct.local and take the first label. Then filter http and read the 200 body for _MULTI.',
    'flag': 'FORENSICS_MULTI',
    'expected_outcome': 'Correlate a DNS query label with HTTP application data to rebuild one submission string',
    'challenge_type': 'network',
    'points': 150,
    'category_id': 8,
    'order_in_category': 5,
}
