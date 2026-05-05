"""
Challenge 10: Network Forensics - Data Exfiltration
Category: Forensics
"""
challenge = {
    'title': 'Network Forensics - Data Exfiltration',
    'description': 'Sensitive data was exfiltrated through DNS queries. Analyze the DNS packets and decode the base64-encoded data hidden in subdomain queries. The flag is the decoded message.',
    'hint': 'Filter for DNS queries. Look at the queried domain names. The data might be encoded in subdomains (e.g., dGhpc2lzYXRlc3Q=.example.com). Extract the base64 part before the domain and decode it.',
    'flag': 'NETWORK_EXFILTRATION_DETECTED',
    'expected_outcome': 'Learn advanced network forensics and DNS tunneling detection',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 8,
    'order_in_category': 1,
}
