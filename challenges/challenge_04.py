"""
Challenge 4: ARP Spoofing Detection
"""
challenge = {
    'title': 'ARP Spoofing Detection',
    'description': 'Detect ARP spoofing in this network capture. Find the MAC address that appears with multiple IP addresses (indicating ARP spoofing). The flag is that MAC address in uppercase with colons removed.',
    'hint': 'In Wireshark, filter for ARP packets using "arp" filter. Look for duplicate MAC addresses associated with different IP addresses. This indicates ARP spoofing. Extract the MAC address.',
    'flag': 'AA1122334455',
    'expected_outcome': 'Learn to detect ARP spoofing attacks through network analysis',
    'challenge_type': 'network',
    'challenge_data': 'MAC address AA:11:22:33:44:55 appears with multiple IPs',
    'order_num': 4
}
