"""
Challenge 3: DNS Query Investigation
Category: DNS
"""
challenge = {
    'title': 'DNS Query Investigation',
    'description': 'Someone made a DNS query. Look for the one whose name starts with the label "FLAG" —the next part is the encoded flag. Decode that part (Base64), then replace dots with underscores and uppercase to get the flag.',
    'hint': 'Filter for DNS packets using the "dns" filter. The queried domain name is under "DNS" → "Queries". Pick the one whose domain starts with "FLAG."—the part after "FLAG." is encoded. Decode that part (Base64), then replace dots with underscores and uppercase to get the flag.',
    'flag': 'DNS_QUERY_FLAG',
    'expected_outcome': 'Learn DNS protocol and how to analyze DNS queries',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 3,
    'order_in_category': 1,
}
