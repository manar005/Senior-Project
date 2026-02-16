"""
Challenge 3: DNS Query Investigation
"""
challenge = {
    'title': 'DNS Query Investigation',
    'description': 'Someone made a DNS query. Look for the one whose name starts with the label "FLAG" (in plain text)—the next part is the encoded flag. Decode that part (Base64), then replace dots with underscores and uppercase to get the flag (e.g., DNS_QUERY_FLAG).',
    'hint': 'Filter for DNS packets in Wireshark using the "dns" filter. The queried domain name is under "DNS" → "Queries" (expand the DNS section, then Queries). Pick the one whose domain starts with "FLAG."—the part after "FLAG." is encoded. Decode that part (Base64), then replace dots with underscores and uppercase to get the flag.',
    'flag': 'DNS_QUERY_FLAG',
    'expected_outcome': 'Learn DNS protocol and how to analyze DNS queries',
    'challenge_type': 'network',
    'order_num': 3
}
