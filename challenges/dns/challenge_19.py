"""
Challenge 19: DNS TXT Record (Multiple Chunks)
Category: DNS

A DNS response contains a TXT record whose value is split into multiple character-string
chunks. Concatenate the chunks in order to get the flag.
"""
challenge = {
    'title': 'DNS TXT Record (Multiple Chunks)',
    'description': 'A DNS response in the capture has a TXT record made of multiple character-string chunks (RFC 1035). Each chunk is a length byte followed by that many characters. Find the TXT record, concatenate all chunks in order, and submit the resulting string as the flag.',
    'hint': 'Filter for DNS and find the response. In the answer section, open the TXT record. Wireshark may show "TXT: chunk1, chunk2, ..." or separate length-prefixed strings. Concatenate them in packet order with no separators to form the flag.',
    'flag': 'CHUNKED_TXT_FLAG',
    'expected_outcome': 'Understand DNS TXT RDATA format (multiple chunks) and reassemble the flag',
    'challenge_type': 'network',
    'points': 120,
    'category_id': 3,
    'order_in_category': 3,
}
