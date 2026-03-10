"""
Challenge 23: FTP Passive Mode Data Connection
Category: FTP
Level 3: Use PASV response to find the data connection and extract the flag from transferred data.
"""
challenge = {
    'title': 'FTP Passive Mode Data Connection',
    'description': 'This capture contains an FTP session using passive (PASV) mode. The client issues PASV and the server responds with an address and port for the data connection. Find the PASV reply, and use e*256+f to find the port number containing the flag.',
    'hint': 'Filter "tcp.port == 2121". In the TCP stream, find the PASV reply (227 Entering Passive Mode). It contains something like (a,b,c,d,e,f) — the data port is e*256+f. Filter or find the TCP stream for that port; the payload contains the flag.',
    'flag': 'PASV_DATA_FLAG',
    'expected_outcome': 'Understand FTP passive mode and correlate control vs data connections',
    'challenge_type': 'network',
    'order_num': 23,
    'points': 100,
    'category_slug': 'ftp',
    'order_in_category': 4,
}
