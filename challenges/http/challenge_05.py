"""
Challenge 5: HTTP Redirect Chain
Category: HTTP
"""
challenge = {
    'title': 'HTTP Redirect Chain',
    'description': 'This capture contains multiple HTTP requests and responses, each in its own TCP stream. One logical flow is a redirect chain: a request gets HTTP 302 with a Location header of the next path. Use Follow → TCP Stream to see the full conversation in order. Follow 302 Location headers from one stream to the next to find which response has the flag. Submit the flag from the X-Flag header of that final response.',
    'hint': 'Look for 302 responses across different TCP streams. The redirect chain is interleaved with other requests. Right click a request → Follow → TCP Stream to follow the Location headers from stream to stream; the response that ends the chain contains the flag in the X-Flag header. The stream goes like this: entry → phase2 → verify → result with X-Flag.',
    'flag': 'REDIRECT_FINAL',
    'expected_outcome': 'Learn how HTTP redirects work and how to trace a redirect chain in captured traffic to find the final response',
    'challenge_type': 'network',
    'points': 150,
    'category_id': 1,
    'order_in_category': 5,
}
