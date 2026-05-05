"""Protocol labels and static copy used by challenges UI."""

PROTOCOL_NAMES = [
    "HTTP",
    "TCP",
    "DNS",
    "FTP",
    "ICMP",
    "SMTP",
    "TLS",
    "Forensics",
]

# Challenge dicts use category_id = challenge_categories.id. With default DB seed order
# (insert_categories in PROTOCOL_NAMES order), ids are 1..8 matching the list above.

PROTOCOL_DETAILS = {
    "HTTP": {
        "overview": "HTTP powers web browsing by carrying requests and responses between clients and servers.",
        "common_ports": "80, 8080",
        "focus": "Methods, headers, status codes, cookies, and suspicious web requests.",
        "why_it_matters": "Understanding HTTP helps you investigate websites, APIs, and common web attacks.",
    },
    "TCP": {
        "overview": "TCP is a reliable transport protocol that manages connection setup, ordering, retransmission, and flow control.",
        "common_ports": "Used by many apps, including 80, 443, 22, and 25",
        "focus": "Three-way handshake, sequence numbers, retransmissions, resets, and fragmentation behavior.",
        "why_it_matters": "TCP analysis is essential for debugging connectivity issues and spotting transport-layer anomalies.",
    },
    "DNS": {
        "overview": "DNS translates domain names into IP addresses so users can reach services by name instead of numbers.",
        "common_ports": "53 UDP and 53 TCP",
        "focus": "Queries, answers, record types, response codes, and unusual domain lookups.",
        "why_it_matters": "DNS traffic often reveals command-and-control activity, data exfiltration, or simple misconfigurations.",
    },
    "FTP": {
        "overview": "FTP transfers files between hosts using separate control and data connections.",
        "common_ports": "21 control, 20 data",
        "focus": "Login attempts, file transfers, directory listings, and credentials sent in clear text.",
        "why_it_matters": "FTP is insecure by default, so it is useful for learning how exposed credentials and file activity appear on the wire.",
    },
    "ICMP": {
        "overview": "ICMP is used for network diagnostics and control messages such as echo requests and unreachable notifications.",
        "common_ports": "No ports - ICMP uses message types and codes",
        "focus": "Echo request/reply, TTL behavior, unreachable errors, and latency troubleshooting.",
        "why_it_matters": "ICMP helps you understand path visibility, host reachability, and reconnaissance behavior.",
    },
    "SMTP": {
        "overview": "SMTP is the protocol used to send email between clients and mail servers.",
        "common_ports": "25, 465, 587",
        "focus": "Mail commands, sender and recipient flow, headers, and attachment delivery patterns.",
        "why_it_matters": "SMTP analysis is valuable for investigating phishing, spoofing, and suspicious outbound mail traffic.",
    },
    "TLS": {
        "overview": "TLS protects application traffic by encrypting communication between endpoints.",
        "common_ports": "Usually carried over TCP 443",
        "focus": "Handshake steps, certificates, SNI, versions, cipher suites, and trust validation.",
        "why_it_matters": "TLS inspection teaches you how secure sessions are established and where weak configurations appear.",
    },
    "Forensics": {
        "overview": "Forensics challenges focus on extracting evidence, reconstructing events, and identifying hidden indicators from captures or files.",
        "common_ports": "Varies by artifact and investigation scope",
        "focus": "Timeline reconstruction, embedded clues, unusual files, and evidence correlation.",
        "why_it_matters": "Forensics skills help you move from raw data to a clear explanation of what happened and why.",
    },
}
