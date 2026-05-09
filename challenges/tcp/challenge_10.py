"""
Challenge 10: Port-Knock Flag
Category: TCP
"""
challenge = {
    'title': 'Port-Knock Flag',
    'description': 'In this capture, a host sent a sequence of TCP SYN packets to different destination ports. The destination port of each SYN, when taken in time order and interpreted as an ASCII character code, spells the flag. Find the SYN packets, list their destination ports in order, convert each port number to its ASCII character, and submit the resulting string as the flag.',
    'hint': 'Filter for initial SYN packets only: tcp.flags.syn==1 and tcp.flags.ack==0. For each packet, note the destination port in the TCP header. Convert each port number to a character (e.g. port 70 = ASCII 70 = "F"). Concatenate the characters in packet order to get the flag.',
    'flag': 'KNOCK_OPEN',
    'expected_outcome': 'Learn to read TCP headers (destination port), follow packet order, and decode port numbers as ASCII to recover a hidden message',
    'challenge_type': 'network',
    'points': 150,
    'category_id': 2,
    'order_in_category': 5,
}
