"""
Challenge 38: ICMP Payload Exfiltration
Category: Forensics
"""
challenge = {
    'title': 'ICMP Payload Exfiltration',
    'description': 'Sensitive data was split across several ICMP Echo Request payloads on loopback. Reconstruct the full secret by reading the hexadecimal data for each exfil packet in chronological order and concatenating the ASCII fragments.',
    'hint': 'Click on each ICMP packet and inspect the hexadecimal data in the lower-right pane. Ignore noise strings; the exfil uses three fragments that form one flag when joined in order.',
    'flag': 'ICMP_EXFIL_38',
    'expected_outcome': 'Extract ASCII from ICMP echo payloads and reassemble a multi-packet exfiltration string',
    'challenge_type': 'network',
    'points': 120,
    'category_id': 8,
    'order_in_category': 3,
}
