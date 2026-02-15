"""
Challenge 3: DNS Query Investigation
"""
challenge = {
    'title': 'DNS Query Investigation',
    'description': 'Someone made a DNS query. What domain name was queried? The flag is the domain name in uppercase with underscores instead of dots (e.g., EXAMPLE_COM).',
    'hint': 'Filter for DNS packets in Wireshark using "dns" filter. Look at DNS query packets. The queried domain name is in the "Question" section. Convert dots to underscores and uppercase it.',
    'flag': 'DNS_QUERY_FLAG',
    'expected_outcome': 'Learn DNS protocol and how to analyze DNS queries',
    'challenge_type': 'network',
    'order_num': 3
}
