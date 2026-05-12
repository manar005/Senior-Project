"""
Challenge 37: HTTP Login Brute Force
Category: Forensics
"""
challenge = {
    'title': 'HTTP Login Brute Force',
    'description': 'An attacker tried to brute-force a web login over HTTP. Multiple POST requests were sent to /login with different passwords for the same username. One of them eventually succeeded. Find the successful attempt, read the password field in the POST body, then decode it: the body is URL-encoded, so you must apply URL decoding to recover the real password. Submit that decoded password as the flag.',
    'hint': 'Filter on POST /login. Match each attempt to its response: failed logins get an error (e.g. 401 and "Invalid credentials."); the successful one gets 200 with a welcome message. In that successful POST, the password= value in the form body is percent-encoded—use a URL decoder (or your tool’s “URL decode” / percent-decode) on that value to get the flag. Do not submit the raw encoded string unless it is already plain text.',
    'flag': 'p@ssw0rd!',
    'expected_outcome': 'Learn how to identify brute-force activity and extract credentials from HTTP login traffic in a pcap file',
    'challenge_type': 'network',
    'points': 100,
    'category_id': 8,
    'order_in_category': 2,
}

