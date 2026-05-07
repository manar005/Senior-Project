import os

from flask import redirect, render_template, request, session, url_for, jsonify

import db_queries

from thaghrah.config import STATIC_DIR
from thaghrah.constants import PROTOCOL_NAMES
from thaghrah.database import get_db
from thaghrah.decorators import login_required


def register_routes(app):
    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("home"))
        return render_template("start.html")

    @app.route("/home")
    @login_required
    def home():
        conn = get_db()
        user_badges = db_queries.get_user_badges(conn, session["user_id"])
        total_badges = db_queries.get_total_badges_count(conn)
        total_points = db_queries.get_user_total_points(conn, session["user_id"])
        conn.close()
        return render_template(
            "home.html",
            user_badges=user_badges,
            total_badges=total_badges,
            total_points=total_points,
        )

    @app.route("/api/me")
    @login_required
    def api_me():
        conn = get_db()
        total_points = db_queries.get_user_total_points(conn, session["user_id"])
        badges = db_queries.get_user_badges(conn, session["user_id"])
        conn.close()
        return jsonify({"points": total_points, "badges": len(badges)})

    @app.route("/guide")
    @login_required
    def guide():
        """
        Reference guides: one entry in ``guide_pages`` per sidebar tab name (must match
        ``PROTOCOL_NAMES`` + "Cheat Sheet"). Reuse the HTTP entry as the template.

        Content shape (each protocol, e.g. guide_pages["TCP"]):
        - ``title``: page H3.
        - ``sections``: list of blocks with optional keys:
          ``heading``, ``paragraphs``, ``bullets``, ``images`` (``src`` under static/,
          ``alt``), ``image_after_paragraph`` (int: render images after that paragraph
          index), ``video`` (``title``, ``embed_url``, ``watch_url``, optional
          ``card_title`` for the bar inside the video card), ``links`` (skipped when
          ``video`` is set).

        Presentation (shared for all protocols—do not duplicate per tab): light reading
        panel, internal scroll, sidebar fixed, ``templates/guide.html`` styles—image /
        video borders, 3rem space below images and video cards, optional PDF block as
        ``Download Guide Here`` with ``download`` attribute. For PDFs: drop the file
        under ``static/pdfs/``, then map tab name → path (see HTTP branch) and set
        ``pdf_available`` / ``selected_pdf`` / ``pdf_download_name``.
        """
        tabs = PROTOCOL_NAMES + ["Cheat Sheet"]
        selected = (request.args.get("tab") or tabs[0]).strip()
        if selected not in tabs:
            selected = tabs[0]
        guide_pages = {
            "HTTP": {
                "title": "HTTP Guide for Thaghrah",
                "sections": [
                    {
                        "heading": "Description",
                        "paragraphs": [
                            "HTTP (Hypertext Transfer Protocol) is the foundational protocol used for communication on the World Wide Web. It defines how clients (such as web browsers) and servers exchange information in a standardized way.",
                            "HTTP follows a client-server, request-response model. The client sends a request to the server, and the server returns a response. It is a stateless protocol — each request is independent, and the server does not retain memory of previous requests unless additional mechanisms (like cookies) are used.",
                            "HTTP is text-based, making it human-readable, and it typically operates on top of TCP. The most common version in use is HTTP/1.1, though modern implementations often use HTTP/2 or HTTP/3 for better performance.",
                        ],
                    },
                    {
                        "heading": "Key Components of HTTP",
                        "paragraphs": [],
                    },
                    {
                        "heading": "1. HTTP Requests",
                        "paragraphs": [
                            "An HTTP request consists of:",
                            "Request Line: Method + URI (path) + HTTP Version. Example: GET /index.html HTTP/1.1",
                            "Headers: Metadata about the request (e.g., Host, User-Agent, Accept, Cookie)",
                            "Body (optional): Data sent with methods like POST or PUT",
                        ],
                        "bullets": [
                            "GET: Retrieve data from the server",
                            "POST: Send data to the server (e.g., form submissions)",
                            "PUT: Replace or create a resource",
                            "DELETE: Remove a resource",
                            "HEAD: Retrieve headers only (no body)",
                        ],
                    },
                    {
                        "heading": "2. HTTP Responses",
                        "paragraphs": [
                            "An HTTP response consists of:",
                        ],
                        "bullets": [
                            "Status Line: HTTP Version + Status Code + Reason Phrase. Example: HTTP/1.1 200 OK",
                            "Headers: Metadata about the response (e.g., Content-Type, Set-Cookie, Location)",
                            "Body (optional): The actual content (HTML, JSON, images, etc.)",
                        ],
                    },
                    {
                        "heading": "3. Status Code Categories",
                        "paragraphs": [
                            "Status codes are grouped into five classes based on the first digit:",
                        ],
                        "images": [
                            {"src": "images/http1.png", "alt": "HTTP status code reference"},
                        ],
                    },
                    {
                        "heading": "4. Important Features",
                        "paragraphs": [],
                        "bullets": [
                            "Cookies: Used to maintain state (session management) across stateless requests. Set by the server via the Set-Cookie header and sent back by the client via the Cookie header.",
                            "Redirects: Server instructs the client to go to another URL using 3xx status codes and the Location header.",
                            "Content Negotiation: Headers like Accept and Content-Type allow clients and servers to agree on data formats.",
                        ],
                    },
                    {
                        "heading": "Visualizations",
                        "paragraphs": [
                            "HTTP Request-Response Cycle",
                            "Watch This: 'HTTP Explained in 3 Minutes'",
                        ],
                        "images": [
                            {"src": "images/http2.png", "alt": "HTTP request-response visualization"},
                        ],
                        "image_after_paragraph": 0,
                        "video": {
                            "title": "HTTP Explained in 3 Minutes",
                            "embed_url": "https://www.youtube.com/embed/KvGi-UDfy00",
                            "watch_url": "https://www.youtube.com/watch?v=KvGi-UDfy00",
                        },
                        "links": [
                            {"label": "Watch on YouTube", "url": "https://www.youtube.com/watch?v=KvGi-UDfy00"},
                        ],
                    },
                ],
            },
            "TCP": {
                "title": "TCP Guide for Thaghrah",
                "sections": [
                    {
                        "heading": "Description",
                        "paragraphs": [
                            "TCP (Transmission Control Protocol) is one of the main protocols of the Internet Protocol Suite (TCP/IP). It operates at the Transport Layer and provides reliable, ordered, and error-checked delivery of data between applications running on different hosts.",
                            "Unlike UDP, TCP is connection-oriented — it establishes a connection before sending data, ensures data arrives correctly and in the right order, and gracefully closes the connection when finished. It is widely used by applications that require reliability, such as web browsing (HTTP), email (SMTP), file transfer (FTP), and remote login.",
                            "TCP achieves reliability through mechanisms like sequence numbers, acknowledgments, retransmission of lost packets, flow control, and congestion control.",
                        ],
                    },
                    {
                        "heading": "Key Components of TCP",
                        "paragraphs": [],
                    },
                    {
                        "heading": "1. TCP Connection Establishment — The 3-Way Handshake",
                        "paragraphs": [
                            "Before any data is sent, TCP performs a three-way handshake to synchronize sequence numbers and establish a reliable connection:",
                        ],
                        "bullets": [
                            "Step 1: Client sends a packet with the SYN (Synchronize) flag.",
                            "Step 2: Server responds with SYN-ACK (Synchronize + Acknowledgment).",
                            "Step 3: Client sends back an ACK (Acknowledgment).",
                        ],
                    },
                    {
                        "heading": "2. TCP Connection Termination — The 4-Way Handshake",
                        "paragraphs": [
                            "To close a connection cleanly, TCP usually performs a four-way handshake:",
                        ],
                        "bullets": [
                            "One side sends a FIN (Finish) flag.",
                            "The other side responds with an ACK.",
                            "The second side then sends its own FIN when ready.",
                            "The first side sends a final ACK.",
                        ],
                    },
                    {
                        "heading": "3. Important TCP Fields and Features",
                        "paragraphs": [],
                        "bullets": [
                            "Ports: 16-bit source and destination port numbers (multiplexing).",
                            "Sequence Number: Tracks the order of bytes sent.",
                            "Acknowledgment Number: Indicates the next byte expected.",
                            "Flags: Control bits including SYN, ACK, FIN, RST (Reset), PSH (Push), URG (Urgent).",
                            "Window Size: Used for flow control (how much data the receiver can accept).",
                            "Checksum: Error detection.",
                        ],
                    },
                    {
                        "heading": "Visualizations",
                        "paragraphs": [
                            "TCP 3-Way Handshake:",
                            "TCP Header Structure:",
                            "Watch This: 'MASTER the TCP/IP Model in 5 Minutes!'",
                        ],
                        "images": [
                            {"src": "images/tcp1.png", "alt": "TCP 3-way handshake visualization", "image_after_paragraph": 0},
                            {"src": "images/tcp2.png", "alt": "TCP header structure visualization", "image_after_paragraph": 1},
                        ],
                        "video": {
                            "title": "MASTER the TCP/IP Model in 5 Minutes!",
                            "embed_url": "https://www.youtube.com/embed/tK61YFdO3Kw",
                            "watch_url": "https://youtu.be/tK61YFdO3Kw?si=H4bSvzGH0nE5DzuX",
                        },
                        "links": [
                            {"label": "Watch on YouTube", "url": "https://youtu.be/tK61YFdO3Kw?si=H4bSvzGH0nE5DzuX"},
                        ],
                    },
                ],
            },
            "DNS": {
                "title": "DNS Guide for Thaghrah",
                "sections": [
                    {
                        "heading": "Description",
                        "paragraphs": [
                            'DNS (Domain Name System) is the "phonebook of the internet." It is a hierarchical and decentralized naming system that translates human-readable domain names (like example.com) into machine-readable IP addresses (like 192.0.2.1).',
                            "DNS makes the internet user-friendly — instead of remembering long IP addresses, we can use easy-to-remember names. It operates as a distributed database, with millions of DNS servers worldwide working together to resolve names quickly and reliably. DNS primarily uses UDP port 53 for queries, but can fall back to TCP port 53 for larger responses or zone transfers.",
                        ],
                    },
                    {
                        "heading": "Key Components of DNS",
                        "paragraphs": [],
                    },
                    {
                        "heading": "1. DNS Resolution Process",
                        "paragraphs": [
                            "When you type a domain name:",
                        ],
                        "bullets": [
                            "Your device asks a DNS Resolver (usually provided by your ISP or public services like Google DNS).",
                            "The resolver performs a series of queries through the DNS hierarchy:",
                            "Root Servers → TLD Servers (e.g., .com, .org) → Authoritative Name Servers for the specific domain.",
                        ],
                    },
                    {
                        "heading": "2. Common DNS Record Types",
                        "paragraphs": [],
                        "images": [
                            {"src": "images/dns1.png", "alt": "Common DNS record types"},
                        ],
                    },
                    {
                        "heading": "3. Important Concepts",
                        "paragraphs": [],
                        "bullets": [
                            "Recursive vs Iterative Queries",
                            "Caching — Results are stored temporarily to speed up future lookups",
                            "Authoritative vs Non-Authoritative Answers",
                            "Zone Files — Where DNS records are stored on servers",
                        ],
                    },
                    {
                        "heading": "Visualizations",
                        "paragraphs": [
                            "DNS Resolution Hierarchy / How DNS Works:",
                            "Watch This: 'DNS Explained in 100 Seconds'",
                        ],
                        "images": [
                            {"src": "images/dns2.png", "alt": "DNS resolution hierarchy visualization", "image_after_paragraph": 0},
                        ],
                        "video": {
                            "title": "DNS Explained in 100 Seconds",
                            "embed_url": "https://www.youtube.com/embed/UVR9lhUGAyU",
                            "watch_url": "https://www.youtube.com/watch?v=UVR9lhUGAyU",
                        },
                        "links": [
                            {"label": "Watch on YouTube", "url": "https://www.youtube.com/watch?v=UVR9lhUGAyU"},
                        ],
                    },
                ],
            },
            "FTP": {
                "title": "FTP Guide for Thaghrah",
                "sections": [
                    {
                        "heading": "Description",
                        "paragraphs": [
                            "FTP (File Transfer Protocol) is a standard network protocol used to transfer files between a client and a server on a computer network. It is one of the oldest protocols still in use today and operates on the Application Layer of the TCP/IP model.",
                            "FTP is a client-server protocol that uses two separate TCP connections:",
                        ],
                        "bullets": [
                            "Control Connection (usually port 21): For sending commands and receiving responses.",
                            "Data Connection (port 20 in active mode, or a dynamic port in passive mode): For actually transferring files and directory listings.",
                        ],
                    },
                    {
                        "heading": "Key Components of FTP",
                        "paragraphs": [
                            "FTP is stateful — it maintains a session with the server until the user logs out or the connection is closed. While powerful, traditional FTP transmits data (including usernames and passwords) in plain text, making it insecure for modern use.",
                        ],
                    },
                    {
                        "heading": "1. Connection Modes",
                        "paragraphs": [],
                        "bullets": [
                            "Active Mode: The client tells the server which port to connect to for data transfer (server initiates the data connection).",
                            "Passive Mode (PASV): The server opens a port and tells the client to connect to it (more firewall-friendly, most commonly used today).",
                        ],
                    },
                    {
                        "heading": "2. Authentication",
                        "paragraphs": [],
                        "bullets": [
                            "Usually requires a username and password.",
                            "Supports anonymous FTP (common username: anonymous or ftp, often with email as password).",
                        ],
                    },
                    {
                        "heading": "3. Common FTP Commands",
                        "paragraphs": [],
                        "bullets": [
                            "USER — Send username",
                            "PASS — Send password",
                            "LIST / NLST — List files and directories",
                            "RETR — Download (Retrieve) a file",
                            "STOR — Upload (Store) a file",
                            "PWD — Print Working Directory",
                            "CWD — Change Working Directory",
                            "QUIT — Logout and close connection",
                        ],
                    },
                    {
                        "heading": "4. File Transfer Types",
                        "paragraphs": [],
                        "bullets": [
                            "ASCII Mode: For text files",
                            "Binary Mode: For images, executables, archives, etc.",
                        ],
                    },
                    {
                        "heading": "Visualizations",
                        "paragraphs": [
                            "FTP Active vs Passive Mode:",
                            "FTP Command Flow:",
                            "Watch This: 'FTP - File Transfer Protocol Animated'",
                        ],
                        "images": [
                            {"src": "images/ftp1.png", "alt": "FTP active vs passive mode visualization", "image_after_paragraph": 0, "max_width": 880},
                            {"src": "images/ftp2.png", "alt": "FTP command flow visualization", "image_after_paragraph": 1, "max_width": 460},
                        ],
                        "video": {
                            "title": "FTP - File Transfer Protocol Animated",
                            "embed_url": "https://www.youtube.com/embed/kKxSiJPQ2kg",
                            "watch_url": "https://youtu.be/kKxSiJPQ2kg?si=TTS4pY7ECTTyAjFS",
                        },
                        "links": [
                            {"label": "Watch on YouTube", "url": "https://youtu.be/kKxSiJPQ2kg?si=TTS4pY7ECTTyAjFS"},
                        ],
                    },
                ],
            },
            "ICMP": {
                "title": "ICMP Guide for Thaghrah",
                "sections": [
                    {
                        "heading": "Description",
                        "paragraphs": [
                            "ICMP (Internet Control Message Protocol) is a supporting protocol in the Internet Protocol Suite. It operates at the Network Layer and is primarily used for error reporting, diagnostics, and network troubleshooting.",
                            "Unlike TCP or UDP, ICMP is not used to transfer application data. Instead, it helps devices communicate information about network problems, such as when a packet cannot be delivered, or to test whether a remote host is reachable. ICMP messages are encapsulated directly within IP packets.",
                            "The most well-known uses of ICMP are the Ping utility (Echo Request/Reply) and Traceroute.",
                        ],
                    },
                    {
                        "heading": "Key Components of ICMP",
                        "paragraphs": [],
                    },
                    {
                        "heading": "1. ICMP Message Structure",
                        "paragraphs": [
                            "Every ICMP message includes:",
                        ],
                        "bullets": [
                            "Type (8 bits) — Defines the main purpose of the message",
                            "Code (8 bits) — Provides additional detail about the Type",
                            "Checksum — For error detection",
                            "Data (variable) — Specific to the message type",
                        ],
                    },
                    {
                        "heading": "2. Most Important ICMP Types",
                        "paragraphs": [],
                        "images": [
                            {"src": "images/icmp2.png", "alt": "Most important ICMP types"},
                        ],
                    },
                    {
                        "heading": "3. Common Use Cases",
                        "paragraphs": [],
                        "bullets": [
                            "Testing reachability (Ping)",
                            "Discovering network paths (Traceroute)",
                            "Reporting delivery errors",
                            "Informing about congestion or routing issues",
                        ],
                    },
                    {
                        "heading": "Visualizations",
                        "paragraphs": [
                            "ICMP Echo Request / Reply (Ping):",
                            "Watch This: 'What is ICMP?'",
                        ],
                        "images": [
                            {"src": "images/icmp1.png", "alt": "ICMP echo request and reply visualization", "image_after_paragraph": 0},
                        ],
                        "video": {
                            "title": "What is ICMP?",
                            "embed_url": "https://www.youtube.com/embed/xTqtm7-k25o",
                            "watch_url": "https://youtu.be/xTqtm7-k25o?si=WRNCvhBKNhXIeY1S",
                        },
                        "links": [
                            {"label": "Watch on YouTube", "url": "https://youtu.be/xTqtm7-k25o?si=WRNCvhBKNhXIeY1S"},
                        ],
                    },
                ],
            },
            "SMTP": {
                "title": "SMTP Guide for Thaghrah",
                "sections": [
                    {
                        "heading": "Description",
                        "paragraphs": [
                            "SMTP (Simple Mail Transfer Protocol) is the standard protocol used for sending and relaying emails across the Internet. It operates at the Application Layer and is responsible for transferring email messages from one mail server to another, or from an email client to a mail server.",
                            "SMTP is a text-based, client-server protocol that uses a simple command-response model. It is primarily designed for sending mail (not retrieving — that’s done by POP3 or IMAP). Like HTTP and FTP, SMTP is human-readable, making it relatively easy to analyze. It typically runs on TCP port 25, with modern secure variants using port 587 (submission) or 465 (SMTPS).",
                        ],
                    },
                    {
                        "heading": "Key Components of SMTP",
                        "paragraphs": [],
                    },
                    {
                        "heading": "1. SMTP Session Flow",
                        "paragraphs": [
                            "A typical SMTP session follows this sequence:",
                        ],
                        "bullets": [
                            "Client connects to the server",
                            "Greeting from server",
                            "Client identifies itself",
                            "Sender and recipient information exchange",
                            "Message transmission",
                            "Session termination",
                        ],
                    },
                    {
                        "heading": "2. Common SMTP Commands",
                        "paragraphs": [],
                        "images": [
                            {"src": "images/smtp2.png", "alt": "Common SMTP commands", "max_width": 820},
                        ],
                    },
                    {
                        "heading": "3. Important Features",
                        "paragraphs": [],
                        "bullets": [
                            "Email Headers: From:, To:, Subject:, Date:, etc.",
                            "Message Body: Plain text or HTML with possible attachments (via MIME)",
                            "Relaying: Servers forward messages toward the final destination",
                            "Status Codes: 3-digit reply codes (e.g., 250 OK, 550 No such user)",
                        ],
                    },
                    {
                        "heading": "Visualizations",
                        "paragraphs": [
                            "SMTP Email Transmission Flow:",
                            "Watch This: 'What Is SMTP ?'",
                        ],
                        "images": [
                            {"src": "images/smtp1.png", "alt": "SMTP email transmission flow visualization", "image_after_paragraph": 0, "max_width": 840},
                        ],
                        "video": {
                            "title": "What Is SMTP ?",
                            "embed_url": "https://www.youtube.com/embed/iUhDT3ZtWS0",
                            "watch_url": "https://youtu.be/iUhDT3ZtWS0?si=iCUJn4E1vnIwKsTX",
                        },
                        "links": [
                            {"label": "Watch on YouTube", "url": "https://youtu.be/iUhDT3ZtWS0?si=iCUJn4E1vnIwKsTX"},
                        ],
                    },
                ],
            },
            "TLS": {
                "title": "TLS Guide for Thaghrah",
                "sections": [
                    {
                        "heading": "Description",
                        "paragraphs": [
                            "TLS (Transport Layer Security) is the standard protocol used to provide secure communication over a computer network. It is the successor to the older SSL (Secure Sockets Layer) protocol and is widely used to encrypt connections, especially for HTTPS websites, email, messaging apps, and more.",
                            "TLS ensures three main security properties:",
                        ],
                        "bullets": [
                            "Confidentiality — Data is encrypted so only the intended recipient can read it.",
                            "Integrity — Data cannot be tampered with during transit.",
                            "Authentication — Verifies that you are communicating with the legitimate server (via certificates).",
                        ],
                    },
                    {
                        "heading": "Key Components of TLS",
                        "paragraphs": [
                            "TLS operates between the Transport Layer (TCP) and Application Layer, adding a security layer to otherwise insecure protocols like HTTP, SMTP, and FTP.",
                        ],
                    },
                    {
                        "heading": "1. TLS Handshake",
                        "paragraphs": [
                            "This is the most important process:",
                        ],
                        "bullets": [
                            "Client and server negotiate the TLS version and cipher suite.",
                            "Server presents its digital certificate for authentication.",
                            "They exchange keys to establish a shared symmetric encryption key.",
                            "Secure encrypted session begins.",
                        ],
                    },
                    {
                        "heading": "2. Certificates and Public Key Infrastructure (PKI)",
                        "paragraphs": [],
                        "bullets": [
                            "Servers present X.509 certificates signed by trusted Certificate Authorities (CAs).",
                            "Certificates contain the server’s public key and identity.",
                        ],
                    },
                    {
                        "heading": "3. Cipher Suites",
                        "paragraphs": [
                            "Combinations of algorithms for:",
                        ],
                        "bullets": [
                            "Key exchange (e.g., ECDHE)",
                            "Authentication",
                            "Encryption (e.g., AES)",
                            "Message Authentication (e.g., SHA-256)",
                        ],
                    },
                    {
                        "heading": "4. TLS Record Protocol",
                        "paragraphs": [
                            "After the handshake, all application data is broken into records, encrypted, and sent with integrity protection.",
                        ],
                    },
                    {
                        "heading": "Visualizations",
                        "paragraphs": [
                            "TLS Handshake Process:",
                            "TLS vs Plain Communication:",
                            "Watch This: 'SSL/TLS Explained in 7 Minutes'",
                        ],
                        "images": [
                            {"src": "images/tls1.png", "alt": "TLS handshake process visualization", "image_after_paragraph": 0},
                            {"src": "images/tls2.png", "alt": "TLS vs plain communication visualization", "image_after_paragraph": 1},
                        ],
                        "video": {
                            "title": "SSL/TLS Explained in 7 Minutes",
                            "embed_url": "https://www.youtube.com/embed/67Kfsmy_frM",
                            "watch_url": "https://youtu.be/67Kfsmy_frM?si=AEVhhPW4Wvo4u5f3",
                        },
                        "links": [
                            {"label": "Watch on YouTube", "url": "https://youtu.be/67Kfsmy_frM?si=AEVhhPW4Wvo4u5f3"},
                        ],
                    },
                ],
            },
            "Forensics": {
                "title": "Network Forensics Guide for Thaghrah",
                "sections": [
                    {
                        "heading": "Description",
                        "paragraphs": [
                            "Network Forensics is the process of capturing, recording, and analyzing network traffic to investigate security incidents, troubleshoot problems, or reconstruct events. It involves examining packet captures (PCAPs) to understand what happened on the network — such as detecting intrusions, tracing data exfiltration, identifying malicious behavior, or recovering lost information.",
                            'Unlike the other protocol-specific categories, Network Forensics challenges combine multiple protocols and require broader investigative thinking. Analysts look at the "big picture" across different layers of the network stack to piece together timelines, user actions, and attacker techniques.',
                        ],
                    },
                    {
                        "heading": "Key Components of Network Forensics",
                        "paragraphs": [],
                    },
                    {
                        "heading": "1. Core Objectives",
                        "paragraphs": [],
                        "bullets": [
                            "Reconstruct events and timelines from network traffic",
                            "Identify sources and destinations of communication",
                            "Detect anomalies, suspicious patterns, or data leaks",
                            "Recover transferred files, credentials, or sensitive information",
                            "Correlate activity across multiple protocols",
                        ],
                    },
                    {
                        "heading": "2. Common Techniques",
                        "paragraphs": [],
                        "bullets": [
                            "Traffic Analysis: Understanding normal vs abnormal behavior",
                            "Protocol Analysis: Examining HTTP, DNS, TCP, FTP, SMTP, TLS, etc.",
                            "Session Reconstruction: Reassembling conversations (e.g., following TCP streams)",
                            "Artifact Recovery: Extracting files, images, or payloads from captures",
                            "Timeline Building: Ordering events based on timestamps",
                        ],
                    },
                    {
                        "heading": "3. Important Concepts",
                        "paragraphs": [],
                        "bullets": [
                            "Indicators of Compromise (IoCs): Suspicious IPs, domains, unusual ports, large data transfers",
                            "Data Exfiltration: Unauthorized transfer of sensitive data out of the network",
                            "Multi-Protocol Correlation: Connecting clues from DNS queries → HTTP requests → FTP uploads, etc.",
                            "Encryption Challenges: Analyzing traffic before/after TLS or identifying encrypted tunnels",
                        ],
                    },
                    {
                        "heading": "Visualizations",
                        "paragraphs": [
                            "Network Forensics Investigation Workflow:",
                            "Multi-Protocol Analysis Overview:",
                            "Watch This: 'What Is Network Forensics?'",
                        ],
                        "images": [
                            {"src": "images/forensics1.png", "alt": "Network forensics investigation workflow", "image_after_paragraph": 0},
                            {"src": "images/forensics2.png", "alt": "Multi-protocol analysis overview", "image_after_paragraph": 1},
                        ],
                        "video": {
                            "title": "What Is Network Forensics?",
                            "embed_url": "https://www.youtube.com/embed/q0X3ZBDxlAs",
                            "watch_url": "https://youtu.be/q0X3ZBDxlAs?si=MbgXs5dwL2qJsKk2",
                        },
                        "links": [
                            {"label": "Watch on YouTube", "url": "https://youtu.be/q0X3ZBDxlAs?si=MbgXs5dwL2qJsKk2"},
                        ],
                    },
                ],
            },
            "Cheat Sheet": {
                "title": "Thaghrah Cheat Sheet",
                "sections": [
                    {
                        "heading": "HTTP",
                        "paragraphs": [],
                        "bullets": [
                            "http -> Show all HTTP traffic",
                            "http.response -> Show only HTTP responses",
                            "http.request -> Show only HTTP requests",
                            "http.response.code == 200 -> Filter successful responses",
                            "http.response.code == 404 -> Filter 404 Not Found responses",
                            "http.response.code == 302 -> Filter redirect responses",
                            "http.request.method == \"POST\" -> Show POST requests",
                            "http.request.method == \"GET\" -> Show GET requests",
                            "http contains \"login\" -> Find login related packets",
                            "http contains \"X-Flag\" -> Search for custom flag headers",
                            "http contains \"Set-Cookie\" -> Find Set-Cookie headers",
                            "http contains \"Cookie:\" -> Find Cookie headers",
                            "http contains \"Location:\" -> Find redirect Location headers",
                        ],
                    },
                    {
                        "heading": "HTTP - Important Wireshark Actions",
                        "paragraphs": [],
                        "bullets": [
                            "Right-click packet -> Follow -> TCP Stream",
                            "Right-click packet -> Follow -> HTTP Stream",
                            "File -> Export Objects -> HTTP",
                        ],
                    },
                    {
                        "heading": "TCP",
                        "paragraphs": [],
                        "bullets": [
                            "tcp -> Show all TCP traffic",
                            "tcp.flags.syn == 1 && tcp.flags.ack == 0 -> Show only initial SYN packets",
                            "tcp.flags.syn == 1 -> Show all packets with SYN flag",
                            "tcp.flags.syn == 1 && tcp.flags.ack == 1 -> Show SYN-ACK packets",
                            "tcp.port == 8888 -> Filter traffic on port 8888",
                            "tcp.port == 9998 -> Filter traffic on port 9998",
                            "tcp.stream eq 0 -> Filter a specific TCP stream (change number as needed)",
                            "tcp.flags -> Display TCP flags",
                            "tcp.len > 0 -> Show packets containing data",
                        ],
                    },
                    {
                        "heading": "TCP - Important Wireshark Actions",
                        "paragraphs": [],
                        "bullets": [
                            "Right-click packet -> Follow -> TCP Stream",
                            "Right-click packet -> Follow -> TCP Stream -> Save as Raw",
                            "Statistics -> Conversations -> TCP",
                        ],
                    },
                    {
                        "heading": "DNS",
                        "paragraphs": [],
                        "bullets": [
                            "dns -> Show all DNS traffic",
                            "dns.flags.response == 0 -> Show only DNS queries",
                            "dns.flags.response == 1 -> Show only DNS responses",
                            "dns.qry.name contains \"FLAG\" -> Find queries with FLAG in the domain name",
                            "dns.resp.type == 16 -> Filter for TXT record responses",
                            "dns.resp.type == 5 -> Filter for CNAME record responses",
                            "dns.count.answers == 2 -> Find responses with multiple answer records",
                            "dns contains \"TXT\" -> Search for TXT records",
                            "dns contains \"CNAME\" -> Search for CNAME records",
                        ],
                    },
                    {
                        "heading": "DNS - Important Wireshark Actions",
                        "paragraphs": [],
                        "bullets": [
                            "Expand DNS section -> Queries or Answers",
                            "Right-click packet -> Follow -> UDP Stream (or TCP if applicable)",
                            "Look under Answers section for record types and values",
                        ],
                    },
                    {
                        "heading": "FTP",
                        "paragraphs": [],
                        "bullets": [
                            "tcp.port == 2121 -> Filter FTP control channel traffic",
                            "ftp -> Show only FTP commands and responses",
                            "ftp.request.command == \"USER\" -> Find username",
                            "ftp.request.command == \"PASS\" -> Find password",
                            "ftp.request.command == \"CWD\" -> Find Change Working Directory commands",
                            "ftp.request.command == \"PASV\" -> Find Passive mode requests",
                            "ftp.response.code == 227 -> Find PASV replies (contains IP and port)",
                            "ftp.request.command == \"RETR\" -> Find file download commands",
                            "ftp.request.command == \"RNFR\" -> Find Rename From commands",
                            "ftp.request.command == \"RNTO\" -> Find Rename To commands",
                        ],
                    },
                    {
                        "heading": "FTP - Important Wireshark Actions",
                        "paragraphs": [],
                        "bullets": [
                            "Right-click packet -> Follow -> TCP Stream",
                            "Follow the control channel (port 2121) first, then calculate and follow data ports from PASV replies",
                            "Look for command-response pairs in the followed stream",
                        ],
                    },
                    {
                        "heading": "ICMP",
                        "paragraphs": [],
                        "bullets": [
                            "icmp -> Show all ICMP traffic",
                            "icmp.type == 8 -> Filter Echo Request packets (Ping)",
                            "icmp.type == 0 -> Filter Echo Reply packets (Ping response)",
                            "icmp.type == 3 -> Filter Destination Unreachable packets",
                            "icmp.type == 11 -> Filter Time Exceeded packets",
                            "icmp.type -> Display ICMP Type field",
                            "icmp.code -> Display ICMP Code field",
                            "icmp.ident -> Display Identifier field (useful for Echo packets)",
                            "icmp.seq -> Display Sequence number field",
                        ],
                    },
                    {
                        "heading": "ICMP - Important Wireshark Actions",
                        "paragraphs": [],
                        "bullets": [
                            "Expand the ICMP section in packet details to see Type, Code, Identifier, and Sequence",
                            "Use Statistics -> Packet Lengths or Statistics -> Resolved Addresses for overview",
                            "Sort packets by time to analyze sequences",
                        ],
                    },
                    {
                        "heading": "SMTP",
                        "paragraphs": [],
                        "bullets": [
                            "tcp.port == 2525 -> Filter SMTP traffic (common in these challenges)",
                            "smtp -> Show only SMTP commands and responses",
                            "smtp.req.command -> Filter SMTP request commands",
                            "smtp.resp.code -> Filter SMTP response codes",
                            "smtp contains \"EHLO\" -> Find EHLO commands",
                            "smtp contains \"HELO\" -> Find HELO commands",
                            "smtp contains \"MAIL FROM\" -> Find sender information",
                            "smtp contains \"RCPT TO\" -> Find recipient information",
                            "smtp contains \"DATA\" -> Find start of mail data",
                            "smtp.resp.code == 354 -> Find \"Start mail input\" reply",
                        ],
                    },
                    {
                        "heading": "SMTP - Important Wireshark Actions",
                        "paragraphs": [],
                        "bullets": [
                            "Right-click packet -> Follow -> TCP Stream (Essential for all SMTP challenges)",
                            "Look for command-response pairs in the followed stream",
                            "Examine headers and body after the DATA command",
                        ],
                    },
                    {
                        "heading": "Forensics",
                        "paragraphs": [],
                        "bullets": [
                            "dns -> Show all DNS traffic",
                            "http -> Show all HTTP traffic",
                            "icmp -> Show all ICMP traffic",
                            "tcp.port == 53 -> Alternative DNS filter",
                            "http.request.method == \"POST\" -> Find login brute force attempts",
                            "http.response.code == 200 -> Successful HTTP responses",
                            "http.response.code == 401 -> Failed login attempts",
                            "dns.qry.name -> Examine queried domain names",
                            "icmp.type == 8 -> ICMP Echo Requests",
                            "frame.time -> Sort packets chronologically",
                        ],
                    },
                    {
                        "heading": "Forensics - Important Wireshark Actions",
                        "paragraphs": [],
                        "bullets": [
                            "Right-click packet -> Follow -> TCP Stream / UDP Stream",
                            "Right-click -> Follow -> HTTP Stream",
                            "Examine packet payload in hexadecimal pane (for ICMP exfiltration)",
                            "Sort packets by Time column for chronological order",
                            "Use Statistics -> Conversations to see multi-protocol activity",
                        ],
                    },
                ],
            },
        }
        page_content = guide_pages.get(selected)
        pdf_available = False
        selected_pdf = None
        guide_pdfs = {
            "HTTP": "pdfs/HTTP Guide.pdf",
            "TCP": "pdfs/TCP Guide.pdf",
            "DNS": "pdfs/DNS Guide.pdf",
            "FTP": "pdfs/FTP Guide.pdf",
            "ICMP": "pdfs/ICMP Guide.pdf",
            "SMTP": "pdfs/SMTP Guide.pdf",
            "TLS": "pdfs/TLS Guide.pdf",
            "Forensics": "pdfs/Forensics.pdf",
            "Cheat Sheet": "pdfs/Cheat Sheet.pdf",
        }
        rel_pdf = guide_pdfs.get(selected)
        if rel_pdf:
            abs_pdf = os.path.join(STATIC_DIR, rel_pdf)
            if os.path.isfile(abs_pdf):
                selected_pdf = rel_pdf
                pdf_available = True

        pdf_download_name = os.path.basename(selected_pdf) if selected_pdf else ""

        return render_template(
            "guide.html",
            tabs=tabs,
            selected_tab=selected,
            page_content=page_content,
            selected_pdf=selected_pdf,
            pdf_available=pdf_available,
            pdf_download_name=pdf_download_name,
        )
