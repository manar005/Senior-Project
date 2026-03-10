"""
Challenge 18: DNS TXT Record Response
Category: DNS

A DNS response in the capture contains a TXT record. The flag is the string value of that TXT record.
"""
challenge = {
    'title': 'DNS TXT Record Response',
    'description': 'A host received a DNS response that includes a TXT record. Find that response in the capture and read the TXT record value—that string is the flag.',
    'hint': 'Filter for DNS with "dns". Look at DNS responses (not just queries). In the response, find an answer section with type TXT. The TXT record holds a single string; submit that exact string as the flag.',
    'flag': 'FLAG_DNS_RESPONSE',
    'expected_outcome': 'Learn to analyze DNS responses and extract data from TXT records',
    'challenge_type': 'network',
    'order_num': 18,
    'points': 100,
    'category_slug': 'dns',
    'order_in_category': 2,
}
