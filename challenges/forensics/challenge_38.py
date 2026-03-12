"""
Challenge 38: Forensics (3/5)
Category: Forensics
"""
challenge = {
    'title': 'Suspicious Domain',
    'description': 'This capture contains DNS or HTTP traffic to several domains. One domain is used for data exfiltration. Find that domain and submit it as the flag.',
    'hint': 'Filter for DNS or HTTP. Look for unusual or long domain names, or domains that appear only once. The exfiltration domain often has encoded data in the name.',
    'flag': 'EXFIL_DOMAIN',
    'expected_outcome': 'Identify a suspicious or exfiltration-related domain from traffic',
    'challenge_type': 'network',
    'order_num': 38,
    'points': 120,
    'category_slug': 'forensics',
    'order_in_category': 3,
}
