"""
Challenge 11: HTTP Login Brute Force
Category: Forensics
"""
challenge = {
    'title': 'HTTP Login Brute Force',
    'description': 'An attacker tried to brute-force a web login over HTTP. Multiple POST requests were sent to /login with different passwords for the same username. One of them eventually succeeded. Analyze the HTTP traffic and find the correct password that was used in the successful login attempt.',
    'hint': 'Filter HTTP traffic and focus on POST requests to /login. Compare the request bodies (username and password) with the server responses. Most attempts return an error (e.g., HTTP 401 with "Invalid credentials."). One attempt returns a successful response (HTTP 200 with a welcome message). The flag is the correct password used in that successful request, formatted exactly as seen in the packet.',
    'flag': 'p@ssw0rd!',
    'expected_outcome': 'Learn how to identify brute-force activity and extract credentials from HTTP login traffic in a pcap file',
    'challenge_type': 'network',
    'order_num': 11,
    'points': 100,
    'category_slug': 'forensics',
    'order_in_category': 2,
}

