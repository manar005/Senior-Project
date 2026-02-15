"""
Challenge 8: Port Scanning Detection
"""
challenge = {
    'title': 'Port Scanning Detection',
    'description': 'A port scan was detected. What port range was scanned? The flag is SCAN_RANGE_X_Y where X is the first port and Y is the last port.',
    'hint': 'Look for multiple connection attempts to different ports from the same source IP. Filter by source IP and look at destination ports. Identify the range of ports that were scanned.',
    'flag': 'SCAN_RANGE_8080_8090',
    'expected_outcome': 'Learn to detect port scanning activities in network traffic',
    'challenge_type': 'network',
    'order_num': 8
}
