"""
Challenge 1: Wireshark Basics - HTTP Traffic
Category: HTTP
"""
challenge = {
    'title': 'Wireshark Basics - HTTP Traffic',
    'description': 'You captured some network traffic. Analyze the HTTP packets to find the secret flag. Download the pcap file and use Wireshark to analyze it.',
    'hint': 'Open the pcap file in Wireshark. Filter for HTTP traffic using "http" filter. Look at HTTP response packets and examine the headers. The flag might be in a custom header or in the response body.',
    'flag': 'NETWORK_HTTP_FLAG',
    'expected_outcome': 'Learn to use Wireshark for packet analysis and understand HTTP protocol structure',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 1,
    'order_in_category': 1,
}
