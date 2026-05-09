"""
Challenge 39: Staged C2
Category: Forensics
"""
challenge = {
    'title': 'Staged C2 (DNS then HTTP)',
    'description': 'Multiple HTTP beacon exchanges appear throughout the capture, each returning similar response bodies. Examine the HTTP sessions carefully, trace the meaningful response, recover the encrypted value it contains, and submit the decoded ASCII string as the flag.',
    'hint': 'Inspect HTTP responses for session values in their body. Decode the Base64-encoded value and submit the resulting ASCII string as the flag.',
    'flag': 'C2_BEACON',
    'expected_outcome': 'Stage DNS with HTTP, then decode an encoded session value to recover the credential',
    'challenge_type': 'network',
    'points': 130,
    'category_id': 8,
    'order_in_category': 4,
}
