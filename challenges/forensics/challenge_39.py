"""
Challenge 39: Forensics (4/5)
Category: Forensics
"""
challenge = {
    'title': 'Timeline Reconstruction',
    'description': 'From this capture, determine the exact time (UTC) of the first packet that matches a given filter. The flag is TIMESTAMP_YYYYMMDD_HHMMSS.',
    'hint': 'Use Wireshark to filter the relevant traffic. Sort by time and note the first packet timestamp. Convert to UTC if needed. Submit as TIMESTAMP_YYYYMMDD_HHMMSS.',
    'flag': 'TIMESTAMP_FLAG',
    'expected_outcome': 'Extract and format a packet timestamp from a capture',
    'challenge_type': 'network',
    'order_num': 39,
    'points': 130,
    'category_slug': 'forensics',
    'order_in_category': 4,
}
