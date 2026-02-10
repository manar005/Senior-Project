"""
Challenge 1: Wireshark Basics - HTTP Traffic
"""
challenge = {
    'title': 'Wireshark Basics - HTTP Traffic',
    'description': 'You captured some network traffic. Analyze the HTTP packets to find the secret flag. The flag is hidden in an HTTP response header. Download the pcap file and use Wireshark to analyze it. Look for HTTP responses and check the headers.',
    'hint': 'Open the pcap file in Wireshark. Filter for HTTP traffic using "http" filter. Look at HTTP response packets and examine the headers. The flag might be in a custom header or in the response body.',
    'flag': 'NETWORK_HTTP_FLAG_2026',
    'expected_outcome': 'Learn to use Wireshark for packet analysis and understand HTTP protocol structure',
    'challenge_type': 'network',
    'challenge_data': 'Analyze HTTP packets in Wireshark. Filter: http. Check response headers.',
    'order_num': 1
}
