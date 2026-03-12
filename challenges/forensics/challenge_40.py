"""
Challenge 40: Forensics (5/5)
Category: Forensics
"""
challenge = {
    'title': 'Multi-Protocol Correlation',
    'description': 'This capture contains multiple protocols (e.g. DNS, HTTP, TCP). A single secret was split across them. Reconstruct the full flag by combining the pieces in the correct order.',
    'hint': 'Identify each protocol stream that carries a piece of the flag. Note the order of events (time order or stream index). Concatenate the pieces to form the complete flag.',
    'flag': 'FORENSICS_FINAL',
    'expected_outcome': 'Correlate multiple protocol streams to reconstruct a single secret',
    'challenge_type': 'network',
    'order_num': 40,
    'points': 150,
    'category_slug': 'forensics',
    'order_in_category': 5,
}
