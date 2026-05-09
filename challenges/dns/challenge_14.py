"""
Challenge 14: DNS CNAME Record
Category: DNS
"""
challenge = {
    'title': 'DNS CNAME Record',
    'description': 'A DNS response in the capture includes a CNAME record. The canonical name (the domain name the CNAME points to) encodes the flag: replace every dot with an underscore and convert the result to uppercase, then submit that string.',
    'hint': 'Filter for DNS and find the response. In the Answers section, look for a record of type CNAME. The "CNAME" field (the target name) is the encoded flag—replace dots with underscores and uppercase to get the flag.',
    'flag': 'FLAG_VIA_CNAME',
    'expected_outcome': 'Learn to read DNS CNAME records and decode the flag from the canonical name',
    'challenge_type': 'network',
    'points': 130,
    'category_id': 3,
    'order_in_category': 4,
}
