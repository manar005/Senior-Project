"""
Challenge 15: DNS CNAME and TXT (Combine)
Category: DNS
"""
challenge = {
    'title': 'DNS CNAME and TXT (Combine)',
    'description': 'One DNS response in the capture has two answer records: first a CNAME, then a TXT. To get the flag: (1) Take the CNAME\'s canonical name (target), replace dots with underscores and convert to uppercase. (2) Append a single underscore. (3) Append the exact string from the TXT record. Submit the combined result.',
    'hint': 'Filter for DNS and find a response with "Answer RRs: 2". Expand Answers: the first record is a CNAME (decode its target: dots→underscores, uppercase). The second is a TXT (use its string as-is). Join them with one underscore between, no spaces.',
    'flag': 'THINK_DNS_FINAL',
    'expected_outcome': 'Combine skills from earlier DNS challenges: read both CNAME and TXT from one response and form the flag',
    'challenge_type': 'network',
    'points': 150,
    'category_id': 3,
    'order_in_category': 5,
}