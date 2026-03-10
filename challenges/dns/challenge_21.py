"""
Challenge 21: DNS CNAME and TXT (Combine)
Category: DNS

A single DNS response contains two answer records: a CNAME and a TXT.
The flag is formed by combining both—decode the CNAME target, then append the TXT value.
"""
challenge = {
    'title': 'DNS CNAME and TXT (Combine)',
    'description': 'One DNS response in the capture has two answer records: first a CNAME, then a TXT. To get the flag: (1) Take the CNAME\'s canonical name (target), replace dots with underscores and convert to uppercase. (2) Append a single underscore. (3) Append the exact string from the TXT record. Submit the combined result.',
    'hint': 'Filter for DNS and find a response with "Answer RRs: 2". Expand Answers: the first record is a CNAME (decode its target: dots→underscores, uppercase). The second is a TXT (use its string as-is). Join them with one underscore between, no spaces.',
    'flag': 'THINK_DNS_FINAL',
    'expected_outcome': 'Combine skills from earlier DNS challenges: read both CNAME and TXT from one response and form the flag',
    'challenge_type': 'network',
    'order_num': 21,
    'points': 150,
    'category_slug': 'dns',
    'order_in_category': 5,
}