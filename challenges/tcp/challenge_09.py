"""
Challenge 9: Image Flag
Category: TCP
"""
challenge = {
    'title': 'Image Flag',
    'description': 'A PNG image containing the flag was sent over a single TCP connection on port 9998. Find the connection, extract the image data from the stream, and open the image to see the flag.',
    'hint': 'Filter by "tcp.port == 9998". Right-click a packet → Follow → TCP Stream. The stream shows the raw PNG bytes from the server. Use "Save as..." and choose Raw format to save the stream. Save it as a .png file and open the image to see the flag.',
    'flag': 'IMAGE_FLAG_9',
    'expected_outcome': 'Learn how to extract binary data (e.g. an image) from a TCP stream in Wireshark',
    'challenge_type': 'network',
    'points': 130,
    'category_id': 2,
    'order_in_category': 4,
}
