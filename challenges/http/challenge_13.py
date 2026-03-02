"""
Challenge 13: HTTP Request Method
Category: HTTP
"""
challenge = {
    'title': 'HTTP Request Method',
    'description': 'This capture contains both GET and POST requests. One response is HTTP 200 OK — that response contains the encoded flag.',
    'hint': 'Find the packet that shows "200 OK" in the Info column — that is the response containing the flag. Click it and look at the packet details for the encoded value. Decode it from Base64 and submit the decoded string.',
    'flag': 'METHOD_POST',
    'expected_outcome': 'Learn to locate an HTTP 200 OK response in a capture, find an encoded flag in that response, and decode it to get the flag',
    'challenge_type': 'network',
    'order_num': 13,
    'points': 100,
    'category_slug': 'http',
    'order_in_category': 3,
}
