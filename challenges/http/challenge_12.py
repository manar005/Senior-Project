"""
Challenge 12: HTTP Status Code
Category: HTTP
"""
challenge = {
    'title': 'HTTP Status Code',
    'description': 'This capture contains several HTTP requests and responses. One response returns HTTP 404 (Not Found). That 404 response contains the flag—in the X-Flag header and in the response body. Find that response and submit the flag you see there.',
    'hint': 'Find the request to /missing; the response to that request is 404. In that response, look at the X-Flag header or the response body — the flag appears there.',
    'flag': 'STATUS_404',
    'expected_outcome': 'Learn to identify HTTP status codes in captured traffic',
    'challenge_type': 'network',
    'order_num': 12,
    'points': 100,
    'category_slug': 'http',
    'order_in_category': 2,
}
