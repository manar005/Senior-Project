"""
Challenge 14: HTTP Cookie Extraction
Category: HTTP
"""
challenge = {
    'title': 'HTTP Cookie Extraction',
    'description': 'This capture shows a user logging in to a web application over HTTP. The client sends POST requests to /login with username and password. After a successful login, the server responds with HTTP 200 and sets a session cookie in the Set-Cookie header. Your goal is to find the successful login response and extract the session cookie value. Submit that cookie value exactly as it appears in the Set-Cookie header.',
    'hint': 'Locate POST requests to /login. Check each response: failed attempts return 401 with no Set-Cookie; the successful attempt returns 200 and includes a Set-Cookie header. You will find the flag there.',
    'flag': 'COOKIE_SESSION_FLAG',
    'expected_outcome': 'Learn how session cookies are set over HTTP and that cookie values are visible in plain text in captured traffic',
    'challenge_type': 'network',
    'order_num': 14,
    'points': 130,
    'category_slug': 'http',
    'order_in_category': 4,
}
