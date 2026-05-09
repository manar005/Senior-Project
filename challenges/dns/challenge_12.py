"""
Challenge 12: DNS TXT Record Response
Category: DNS
"""
challenge = {
    'title': 'DNS TXT Record Response',
    'description': 'A host received a DNS response that includes a TXT record. Find that response in the capture and read the TXT record value—that string is the flag.',
    'hint': 'Filter for DNS with "dns". Look at DNS responses (not just queries). In the response, find an answer section with type TXT. The TXT record holds a single string; submit that exact string as the flag.',
    'flag': 'FLAG_DNS_RESPONSE',
    'expected_outcome': 'Learn to analyze DNS responses and extract data from TXT records',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 3,
    'order_in_category': 2,
}
