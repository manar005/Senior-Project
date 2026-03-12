"""
Challenge 31: SMTP (3/5)
Category: SMTP
"""
challenge = {
    'title': 'SMTP Reply Code',
    'description': 'The SMTP server in this capture sends numeric reply codes. One reply has a specific code that appears in the described way. The flag is REPLY_XXX where XXX is that three-digit code.',
    'hint': 'Filter for the SMTP port and look at server responses. Note the numeric code at the start of each reply line. Find the reply that appears exactly once and submit REPLY_XXX.',
    'flag': 'REPLY_354',
    'expected_outcome': 'Identify SMTP reply codes from server responses',
    'challenge_type': 'network',
    'order_num': 31,
    'points': 120,
    'category_slug': 'smtp',
    'order_in_category': 3,
}
