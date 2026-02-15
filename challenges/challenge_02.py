"""
Challenge 2: TCP Handshake Analysis
"""
challenge = {
    'title': 'TCP Handshake Analysis',
    'description': 'A suspicious connection was made. Analyze the TCP three-way handshake in the captured packets. What is the destination port number? Convert it to hexadecimal and that\'s your flag (format: PORT_0xXXXX).',
    'hint': 'In Wireshark, look for TCP SYN packets. The destination port is in the TCP header. Common ports: 80 (HTTP), 443 (HTTPS), 22 (SSH), 21 (FTP). Convert the decimal port to hex (e.g., 80 = 0x50).',
    'flag': 'PORT_0x1F90',
    'expected_outcome': 'Understand TCP handshake process and port identification',
    'challenge_type': 'network',
    'order_num': 2
}
