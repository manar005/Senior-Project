"""
Challenge 30: SMTP Full Dialog
Category: SMTP
"""
challenge = {
    'title': 'SMTP Full Dialog',
    'description': 'Reconstruct the full SMTP dialog from this capture. The flag is the concatenation of the first digit of each server reply code in order. Submit as SMTP_ followed by that string.',
    'hint': 'Filter for SMTP traffic. List all server replies in time order; take the first digit of each three-digit code and concatenate. Submit as SMTP_ followed by that string.',
    'flag': 'SMTP_2223222',
    'expected_outcome': 'Reconstruct and summarize a full SMTP server reply sequence',
    'challenge_type': 'network',
    'points': 150,
    'category_id': 6,
    'order_in_category': 5,
}
