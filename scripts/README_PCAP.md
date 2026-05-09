# Creating pcap files for network challenges

Capture on **loopback** (e.g. `127.0.0.1` / Loopback adapter) unless noted. Save files under `static/pcaps/` as `challenge_XX.pcapng` (e.g. `challenge_01.pcapng`).

**Script naming:** Files follow `protocol_challengeNN.py` where **NN** matches `static/pcaps/challenge_NN.pcapng` (same **NN** as the download link in the app). Curriculum step numbers in prose below may differ from **NN**; always save using the **NN** that matches your challenge’s pcap.

**Quick reference:** Run all scripts from the **project root**: `python3 scripts/<script_name>.py` (or `python` on Windows). Most scripts expect you to start a Wireshark capture on loopback **before** running the script, then save as `static/pcaps/challenge_XX.pcapng`. **Exceptions:** `forensics_challenge38.py`, `forensics_challenge39.py`, and `forensics_challenge40.py` use Scapy and **write** `static/pcaps/challenge_{38,39,40}.pcapng` directly (requires `pip install scapy`).

### Step-by-step index

| # | Challenge | Script |
|---|-----------|--------|
| 1 | HTTP Flag in Header | `http_challenge01.py` + curl/browser |
| 2 | TCP Destination Port | `tcp_challenge06.py` + curl |
| 3 | DNS Query Flag | `dns_challenge11.py` |
| 4 | FTP Credential Extraction | `ftp_challenge16.py` |
| 5 | ICMP Packet Analysis | `icmp_challenge21.py` |
| 6 | SMTP Protocol | `smtp_challenge26.py` |
| 7 | TCP Handshake Count | `tcp_challenge07.py` |
| 8 | TCP Fragmentation | `tcp_challenge08.py` |
| 9 | Image Flag | `tcp_challenge09.py` |
| 10 | DNS Exfiltration | `forensics_challenge36.py` |
| 11 | HTTP Login Brute Force | `forensics_challenge37.py` |
| 38 | Forensics ICMP exfil | `forensics_challenge38.py` (scapy → pcap) |
| 39 | Forensics DNS → HTTP staging | `forensics_challenge39.py` (scapy → pcap) |
| 40 | Forensics DNS + HTTP (2-part) | `forensics_challenge40.py` (scapy → pcap) |
| 12 | HTTP Status Code | `http_challenge02.py` |
| 13 | HTTP Request Method | `http_challenge03.py` |
| 14 | HTTP Cookie | `http_challenge04.py` |
| 15 | HTTP Redirect Chain | `http_challenge05.py` |
| 16 | TLS Decryption | `tls_challenge31.py` |
| 17 | Port-Knock Flag | `tcp_challenge10.py` |
| 18 | DNS TXT Response | `dns_challenge12.py` |
| 19 | DNS TXT Chunks | `dns_challenge13.py` |
| 20 | DNS CNAME | `dns_challenge14.py` |
| 21 | DNS CNAME and TXT | `dns_challenge15.py` |
| 22 | FTP CWD Reversed | `ftp_challenge17.py` |
| 23 | FTP PASV Data | `ftp_challenge18.py` |
| 24 | FTP RETR File | `ftp_challenge19.py` |
| 25 | FTP Rename (RNFR/RNTO) | `ftp_challenge20.py` |
| 26 | ICMP Type and Code | `icmp_challenge22.py` (sudo + scapy) |
| 27 | ICMP Echo Identifier | `icmp_challenge23.py` (sudo + scapy) |
| 28 | Multiple ICMP Types | `icmp_challenge24.py` (sudo + scapy) |
| 29 | ICMP Type Message | `icmp_challenge25.py` (sudo + scapy) |

---

## Challenge 1 – HTTP Flag in Header

**Flag (submission):** `NETWORK_HTTP_FLAG` (in the HTTP response header **FLAG**).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the server** (from the project root); leave it running:
   ```bash
   python3 scripts/http_challenge01.py
   ```
   The server listens on **127.0.0.1:8765** and sends the flag in the **FLAG** response header.
3. **In another terminal**, request the page (or use a browser):
   ```bash
   curl -i http://127.0.0.1:8765/
   ```
   Or open http://127.0.0.1:8765/ in a browser.
4. **Stop the capture** in Wireshark and **save** as **`static/pcaps/challenge_01.pcapng`**.
5. Stop the server (Ctrl+C in the server terminal).

### What to check

- Filter by **`http`** or **`tcp.port == 8765`**. Find the HTTP response; in the headers you will see **FLAG: NETWORK_HTTP_FLAG**. Submit **NETWORK_HTTP_FLAG**.

---

## Challenge 2 – TCP Destination Port

**Flag (submission):** `PORT_1F90` (destination port in hex: 8080 = 0x1F90).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the server** (from the project root); leave it running:
   ```bash
   python3 scripts/tcp_challenge06.py
   ```
   The server listens on **127.0.0.1:8080**.
3. **In another terminal**, connect (e.g. with curl or browser):
   ```bash
   curl http://127.0.0.1:8080/
   ```
4. **Stop the capture** and **save** as **`static/pcaps/challenge_06.pcapng`**. Stop the server (Ctrl+C).

### What to check

- Filter by **`tcp.port == 8080`**. In the TCP header of the connection from client to server, the **Destination port** is **8080**. In hex that is **1F90**. Submit **PORT_1F90**.

---

## Challenge 3 – DNS Query Flag

**Flag (submission):** `DNS_QUERY_FLAG` (domain has a label that is Base64 of "dns.query.flag"; decode, then replace dots with underscores and uppercase).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface (or the interface your DNS uses; if you use a local resolver, capture there).
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/dns_challenge11.py
   ```
   The script performs a **getaddrinfo** for a domain like **FLAG.**\<base64\>**.local**. The second label is Base64-encoded "dns.query.flag".
3. **Stop the capture** and **save** as **`static/pcaps/challenge_11.pcapng`**.

### What to check

- Filter by **`dns`**. Find the DNS query; the queried name has a label that is Base64. Decode it to get "dns.query.flag"; replace dots with underscores and uppercase to get **DNS_QUERY_FLAG**. Submit **DNS_QUERY_FLAG**.

### Note

If your system resolver sends DNS to a remote server, capture on the interface that carries that traffic, or temporarily point `/etc/hosts`/DNS to 127.0.0.1 and run a local DNS server that logs the query.

---

## Challenge 4 – FTP Credential Extraction

**Flag (submission):** Base64 of `ADMIN_SECRET123` → `QURNSU5fU0VDUkVUMTIz`  
**In the capture:** Plaintext FTP login (USER ADMIN, PASS SECRET123).

### Steps

1. **Start Wireshark** and begin a capture on the loopback interface (e.g. **Loopback** or **Adapter for loopback traffic**).
2. **Run the script** (from the project root):
   ```bash
   python scripts/ftp_challenge16.py
   ```
   The script starts a minimal FTP server on `127.0.0.1:2121`, then an FTP client connects and logs in with **ADMIN** / **SECRET123**. The whole run is short (about a second).
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_16.pcapng`** (File → Save As…).

### What to check

- **Use filter `tcp.port == 2121`** (not `ftp`—Wireshark’s "ftp" only matches port 21; this script uses 2121).
- You should see TCP packets whose payload contains **USER ADMIN** and **PASS SECRET123** in plaintext.
- Solver flow: find credentials → form `ADMIN_SECRET123` → Base64‑encode → submit `QURNSU5fU0VDUkVUMTIz`.

### Port note

The script uses port **2121** so it does not require administrator/root. If something else uses 2121, change `PORT` in `scripts/ftp_challenge16.py`.

---

## Challenge 5 – ICMP Packet Analysis

**Flag (submission):** `ICMP_TYPE_8` (ICMP Echo Request type code).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface (e.g. **Loopback** or **Adapter for loopback traffic**).
2. **Run the script** (from the project root):
   ```bash
   python scripts/icmp_challenge21.py
   ```
   The script sends one ping (ICMP Echo Request, type 8) to `127.0.0.1`.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_21.pcapng`** (File → Save As…).

### What to check

- Filter by **`icmp`**. You should see at least one **Echo (ping) request** (type 8) and possibly an **Echo reply** (type 0).
- Solver finds the ICMP type in the packet (e.g. 8) and submits **ICMP_TYPE_8**.

### Note

On some systems, ICMP to 127.0.0.1 may be handled internally and not appear on the loopback capture. If the capture is empty after running the script, run `ping -n 1 127.0.0.1` (Windows) or `ping -c 1 127.0.0.1` (Linux/macOS) manually while capturing, or capture on your main network adapter and ping an external host (e.g. 8.8.8.8) once—then look for the Echo Request (type 8) in the capture.

---

## Challenge 6 – Network Protocol Identification

**Flag (submission):** `SMTP` (the application layer protocol name in uppercase).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface (e.g. **Loopback** or **Adapter for loopback traffic**).
2. **Run the script** (from the project root):
   ```bash
   python scripts/smtp_challenge26.py
   ```
   The script starts a minimal SMTP server on `127.0.0.1:2525`, then a client connects and sends HELO and QUIT (SMTP dialog).
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_26.pcapng`** (File → Save As…).

### What to check

- Filter by **`tcp.port == 2525`** to see the SMTP traffic. You should see "220 ... ESMTP", "HELO client", "250 Hello", "QUIT", "221 Bye" in the payload.
- Wireshark may decode it as SMTP if you use **Right‑click → Decode As… → SMTP** for the connection, or the payload alone is enough to identify the protocol as **SMTP**.
- Solver identifies the protocol and submits **SMTP**.

### Port note

The script uses port **2525** (SMTP alternate) so it does not require administrator/root. Standard SMTP is port 25.

---

## Challenge 7 – TCP Handshake Count

**Flag (submission):** `HANDSHAKES_3` (number of complete TCP three-way handshakes).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface (e.g. **Loopback** or **Adapter for loopback traffic**).
2. **Run the script** (from the project root):
   ```bash
   python scripts/tcp_challenge07.py
   ```
   The script opens **3 TCP connections** to **127.0.0.1:9999** (server accepts 3, then exits). Each connection produces one complete three-way handshake (SYN → SYN,ACK → ACK).
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_07.pcapng`** (File → Save As…).

### What to check

- Filter by **`tcp`**. Count **complete three-way handshakes**: one [SYN], one [SYN, ACK], one [ACK] per connection.
- Solver submits **HANDSHAKES_3**.

---

## Challenge 8 – TCP Fragmentation

**Flag (submission):** `REASSEMBLE_ME` (reassemble the fragments from the TCP streams).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/tcp_challenge08.py
   ```
   The script opens **4 separate TCP connections** to **127.0.0.1:8888**; each connection sends one fragment (REAS, SEMB, LE_M, E). So each "Follow TCP Stream" shows only one fragment.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_08.pcapng`** (File → Save As…).

### What to check

- Filter by **`tcp.port == 8888`**. Use **Follow → TCP Stream** on each connection (stream 0, 1, 2, 3); each stream shows one fragment. Concatenate in order to get **REASSEMBLE_ME**.

---

## Challenge 9 – Image Flag

**Flag (submission):** `IMAGE_FLAG_9` (extract the image from the TCP stream and open it to see the flag).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Install Pillow** if needed: `pip install Pillow`
3. **Run the script** (from the project root):
   ```bash
   python scripts/tcp_challenge09.py
   ```
   The script creates a small PNG image displaying the flag and sends it over **one TCP connection** to **127.0.0.1:9998**.
4. **Stop the capture** in Wireshark.
5. **Save** the capture as **`static/pcaps/challenge_09.pcapng`** (File → Save As…).

### What to check

- Filter by **`tcp.port == 9998`**. There is a single TCP connection. Use **Follow → TCP Stream** on it. The stream contains the raw PNG bytes from the server. Use **Save as…** → **Raw** to save the stream, then save the file with a `.png` extension. Open the image to see the flag **IMAGE_FLAG_9**.
- Solver flow: filter tcp.port == 9998 → Follow TCP Stream → Save as Raw → save as .png → open image → submit **IMAGE_FLAG_9**.

### Port note

The script uses port **9998** so it does not conflict with challenge 8 (port 8888).

---

## Challenge 10 – Network Forensics (DNS Exfiltration)

**Flag (submission):** `NETWORK_EXFILTRATION_DETECTED` (Base64-decoded from the subdomain in the DNS query).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/forensics_challenge36.py
   ```
   The script runs a minimal DNS server on **127.0.0.1:53535** and a client that queries several domains; one query contains a subdomain that is Base64-encoded "NETWORK_EXFILTRATION_DETECTED" (without padding).
3. **Stop the capture** and **save** as **`static/pcaps/challenge_36.pcapng`**.

### What to check

- Filter by **`dns`**. Find the query whose name has a long label (e.g. **TkVUV09SS19FWEZJTFRSQVRJT05fREVURUNURUQ**). That is Base64; add padding if needed, decode to get **NETWORK_EXFILTRATION_DETECTED**. Submit that string.

---

## Challenge 11 – HTTP Login Brute Force

**Flag (submission):** `p@ssw0rd!` (the correct password used in the successful login attempt).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/forensics_challenge37.py
   ```
   The script starts a simple HTTP server on `127.0.0.1:8081` with a `/login` endpoint, then a client sends several `POST /login` requests with different passwords for the **operator** user. Several attempts return `401 Invalid credentials.`; one attempt (the 5th) with the correct password returns `200 Login successful. Welcome, operator!` Two more failed attempts follow after the success.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_37.pcapng`** (File → Save As…).

### What to check

- Filter by **`tcp.port == 8081`** or **`http`**. Look for `POST /login` requests.
- Inspect the request bodies (e.g., using the **HTTP** tab or raw payload) to see the username and password fields, and compare them with the server responses.
- Most attempts get a `401` response with the body `"Invalid credentials."`. One attempt (in the middle of the sequence, with two more failed attempts after it) gets `200 OK` with `"Login successful. Welcome, operator!"`.
- The flag is the password value in that successful request, formatted exactly as seen: **`p@ssw0rd!`**.

---

## Challenge 38 – Forensics (ICMP payload exfiltration)

**Flag (submission):** `ICMP_EXFIL_38` (concatenate ICMP Echo data fragments in time order).

### Steps

1. **Requires** `scapy` (`pip install scapy` or install project requirements).
2. From the project root, generate the capture (writes **`static/pcaps/challenge_38.pcapng`** directly):
   ```bash
   python scripts/forensics_challenge38.py
   ```

### What to check

- Filter **`icmp`** (or **`icmp.type == 8`**). Ignore noise payloads; read the ICMP **data** field for the three exfil fragments and concatenate in **chronological order** to form **`ICMP_EXFIL_38`**.

---

## Challenge 39 – Forensics (DNS staging → HTTP C2)

**Flag (submission):** `C2_BEACON` (Base64-decode the **`session=`** value from the **staged** HTTP **200** body—the value on the wire is **not** plaintext).

### Steps

1. **Requires** `scapy`.
2. From the project root:
   ```bash
   python scripts/forensics_challenge39.py
   ```
   Writes **`static/pcaps/challenge_39.pcapng`**.

### What to check

- **DNS:** A query for **`staging.c2-sim.local`** appears before the real HTTP.
- **Decoys:** HTTP to **`metrics.telemetry.io`** with **`session=<Base64>`** (no matching DNS for that host); orphan DNS for **`updates.badcdn.local`** and **`collector.telemetry.net`** without follow-up HTTP here.
- **Real:** **`Host: staging.c2-sim.local`**, body **`session=QzJfQkVBQ09O`** (Base64 of **`C2_BEACON`**). Decode and submit **`C2_BEACON`**.

---

## Challenge 40 – Forensics (DNS + HTTP, two parts)

**Flag (submission):** `FORENSICS_MULTI` = **`FORENSICS`** (DNS first label) + **`_MULTI`** (HTTP response body prefix on **`capstone.local`**). Body may include **`verify=len:15`** on a second line.

### Steps

1. **Requires** `scapy`.
2. From the project root:
   ```bash
   python scripts/forensics_challenge40.py
   ```
   Writes **`static/pcaps/challenge_40.pcapng`**.

### What to check

- **DNS:** Query **`FORENSICS.reconstruct.local`** → first label **`FORENSICS`**. Decoy **`noise.placeholder.net`**.
- **HTTP (8088):** Decoy **`wrong.local`**. Real **`capstone.local`** **`GET /flag`** — response body starts with **`_MULTI`**, then **`verify=len:15`**.
- Concatenate: **`FORENSICS`** + **`_MULTI`** = **`FORENSICS_MULTI`**.

---

## Challenge 12 – HTTP Status Code

**Flag (submission):** `STATUS_404` (find the response that returned HTTP 404 and submit in this format).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/http_challenge02.py
   ```
   The script starts an HTTP server on `127.0.0.1:8776`. A client requests `/`, `/about`, `/missing`, and `/index`. The server returns **200** for `/`, `/about`, and `/index`; it returns **404** for `/missing`.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_02.pcapng`** (File → Save As…).

### What to check

- Filter by **`http`** or **`tcp.port == 8776`**. Find the response to **GET /missing** (status 404). The flag **STATUS_404** appears in that response’s **X-Flag** header and in the response body. Submit **STATUS_404**.

---

## Challenge 13 – HTTP Request Method

**Flag (submission):** `METHOD_POST` (found in the response to the POST request).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/http_challenge03.py
   ```
   The script starts an HTTP server on `127.0.0.1:8777`. A client sends **GET /** and **GET /page**, then **POST /submit**. The response to **POST /submit** contains the flag **Base64-encoded** in the X-Flag header and body.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_03.pcapng`** (File → Save As…).

### What to check

- Filter by **`http`** or **`tcp.port == 8777`**. Find **POST /submit**, then **Follow → TCP Stream**. In the response you will see the encoded flag (Base64) in the X-Flag header and body. Decode it and submit **METHOD_POST**.

---

## Challenge 14 – HTTP Cookie Extraction

**Flag (submission):** `COOKIE_SESSION_FLAG` (the session cookie value from the Set-Cookie header after successful login).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/http_challenge04.py
   ```
   The script starts an HTTP server on `127.0.0.1:8778` with a `/login` endpoint. A client sends several `POST /login` requests with username **admin** and different passwords. Failed attempts return **401** with no Set-Cookie; the successful attempt (4th) returns **200** with **Set-Cookie: session=COOKIE_SESSION_FLAG; Path=/; HttpOnly**.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_04.pcapng`** (File → Save As…).

### What to check

- Filter by **`http`** or **`tcp.port == 8778`**. Find **POST /login** requests and inspect each response.
- The successful response is **200 OK** and includes a **Set-Cookie** header. The flag is the **cookie value** only (the part after `session=` and before the first `;`), i.e. **COOKIE_SESSION_FLAG**.
- Submit **COOKIE_SESSION_FLAG** (exactly as in the header).

---

## Challenge 15 – HTTP Redirect Chain

**Flag (submission):** `REDIRECT_FINAL` (found in the final response of the redirect chain only).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/http_challenge05.py
   ```
   The script starts an HTTP server on `127.0.0.1:8779`. The client sends **separate connections** in this order: **GET /entry** (302 → /phase2), **GET /about** (200), **GET /phase2** (302 → /verify), **GET /help** (200), **GET /verify** (302 → /result), **GET /contact** (200), **GET /result** (200 with **X-Flag: REDIRECT_FINAL**). So /about and /help appear in between the redirect steps; the chain is spread across streams.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_05.pcapng`** (File → Save As…).

### What to check

- Filter by **`http`** or **`tcp.port == 8779`**. Each request is a separate TCP stream. Find streams with **302** responses; the chain is interleaved with **GET /about**, **GET /help**, **GET /contact** (all 200). Follow **Location** from one stream to the next: /entry → /phase2 → /verify → /result. The stream with **GET /result** and **200 OK** contains **X-Flag: REDIRECT_FINAL**. Submit **REDIRECT_FINAL**.

---

## Challenge 16 – TLS Decryption

**Flag (submission):** `TLS_DECRYPT_16` (visible after decrypting TLS with the provided private key).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/tls_challenge31.py
   ```
   The script generates a key/cert if needed, starts a TLS server on **127.0.0.1:9443**, and a client connects to receive the flag. The private key is written to **static/keys/challenge_31_private.pem** (for solvers to download).
3. **Stop the capture** and **save** as **`static/pcaps/challenge_31.pcapng`**.

### What to check

- In Wireshark: **Edit → Preferences → Protocols → TLS → RSA keys list** → Add: IP **127.0.0.1**, Port **9443**, Protocol **http**, Key file **static/keys/challenge_31_private.pem**. Reload the pcap; the TLS stream decrypts. The application data contains **FLAG: TLS_DECRYPT_16**. Submit **TLS_DECRYPT_16**.

### Note

Requires **OpenSSL** for key generation. The script uses TLS 1.2 with RSA key exchange so Wireshark can decrypt with the server key.

---

## Challenge 17 – Port-Knock Flag

**Flag (submission):** `KNOCK_OPEN` (destination ports of the SYN packets, in order, spell the flag as ASCII).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/tcp_challenge10.py
   ```
   The script tries to connect to **127.0.0.1** on a sequence of ports (75, 78, 79, 67, 75, 95, 79, 80, 69, 78). No server is listening, so each attempt sends a **TCP SYN** and then gets RST or times out. The **destination port** of each SYN, in packet order, is the ASCII code for **K N O C K _ O P E N**.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_10.pcapng`** (File → Save As…).

### What to check

- Filter for initial SYNs: **`tcp.flags.syn==1 and tcp.flags.ack==0`**. For each packet, note the **Destination port** in the TCP header (75, 78, 79, 67, 75, 95, 79, 80, 69, 78). Convert each to ASCII (e.g. 75 = K, 78 = N, …) and concatenate to get **KNOCK_OPEN**.
- Solver submits **KNOCK_OPEN**.

---

## Challenge 18 – DNS TXT Response

**Flag (submission):** `FLAG_DNS_RESPONSE` (in the TXT record of the DNS response).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/dns_challenge12.py
   ```
   The script runs a minimal DNS server on **127.0.0.1:5300** that responds to a query with a TXT record containing the flag.
3. **Stop the capture** and **save** as **`static/pcaps/challenge_12.pcapng`**.

### What to check

- Filter by **`dns`**. Find the DNS response; the **TXT** answer contains **FLAG_DNS_RESPONSE**. Submit **FLAG_DNS_RESPONSE**.

---

## Challenge 19 – DNS TXT Chunks

**Flag (submission):** As defined in the challenge (TXT record(s) from the DNS server).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/dns_challenge13.py
   ```
   The script runs a DNS server on **127.0.0.1:5301** that responds with TXT record(s) containing the flag (possibly split across labels/records).
3. **Stop the capture** and **save** as **`static/pcaps/challenge_13.pcapng`**.

### What to check

- Filter by **`dns`**. Inspect the DNS response TXT record(s) and reassemble/concatenate if needed to get the flag.

---

## Challenge 20 – DNS CNAME

**Flag (submission):** As defined in the challenge (CNAME target or related record).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/dns_challenge14.py
   ```
   The script runs a DNS server on **127.0.0.1:5302** that responds with CNAME (and possibly other) records.
3. **Stop the capture** and **save** as **`static/pcaps/challenge_14.pcapng`**.

### What to check

- Filter by **`dns`**. Find the response and the CNAME record; the flag is derived from the CNAME target or instructions in the challenge.

---

## Challenge 21 – DNS CNAME and TXT

**Flag (submission):** As defined in the challenge (from CNAME/TXT response).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/dns_challenge15.py
   ```
   The script runs a DNS server on **127.0.0.1:5303** that responds with CNAME and TXT records.
3. **Stop the capture** and **save** as **`static/pcaps/challenge_15.pcapng`**.

### What to check

- Filter by **`dns`**. Inspect the response for CNAME and TXT; combine or decode as per the challenge to get the flag.

---

## Challenge 22 – FTP CWD Reversed Flag

**Flag (submission):** `FTP_REVERSED` (CWD argument is Base64 of reversed flag; decode Base64 then reverse).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/ftp_challenge17.py
   ```
   The script runs an FTP server on **127.0.0.1:2121**; a client logs in and sends **CWD** with a Base64-encoded reversed flag.
3. **Stop the capture** and **save** as **`static/pcaps/challenge_17.pcapng`**.

### What to check

- Filter by **`tcp.port == 2121`**. Find the **CWD** command; the argument is Base64. Decode it, reverse the string, and submit **FTP_REVERSED**.

---

## Challenge 23 – FTP PASV Data

**Flag (submission):** `PASV_DATA_FLAG` (in the data connection payload after PASV + LIST).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/ftp_challenge18.py
   ```
   The script runs an FTP server on **127.0.0.1:2121** (control). Client uses **PASV** then **LIST**; the flag is sent on the **data** connection (port in 227 reply).
3. **Stop the capture** and **save** as **`static/pcaps/challenge_18.pcapng`**.

### What to check

- Filter by **`tcp.port == 2121`** for control. Find the **227** reply (PASV) and note the data port. Filter or follow the **TCP stream** for that data port; the LIST payload contains **PASV_DATA_FLAG**.

---

## Challenge 24 – FTP RETR File

**Flag (submission):** `RETR_FILE_FLAG` (the accepted flag inside the file retrieved via RETR).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/ftp_challenge19.py
   ```
   The script runs an FTP server that serves a file via **RETR**; the file content contains the flag (and possibly other strings; only **RETR_FILE_FLAG** is accepted).
3. **Stop the capture** and **save** as **`static/pcaps/challenge_19.pcapng`**.

### What to check

- Find the **FTP data** connection (PASV port from 227). Follow that TCP stream; the retrieved file content contains **RETR_FILE_FLAG**. Submit **RETR_FILE_FLAG**.

---

## Challenge 25 – FTP Rename (RNFR/RNTO)

**Flag (submission):** As defined in the challenge; one **RNTO** argument is Base64 that decodes to the flag.

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python3 scripts/ftp_challenge20.py
   ```
   The script runs an FTP server; client sends **RNFR**/ **RNTO** commands; one RNTO argument is Base64-encoded flag.
3. **Stop the capture** and **save** as **`static/pcaps/challenge_20.pcapng`**.

### What to check

- Filter by **`tcp.port == 2121`**. Find **RNTO** commands; decode each argument from Base64; one decodes to the flag. Submit that value.

---

## Challenge 26 – ICMP Type and Code

**Flag (submission):** `ICMP_3_1` (one ICMP packet has Type=3, Code=1 — Destination Unreachable, Host Unreachable).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Install Scapy** if needed: `pip3 install scapy` (on macOS use `pip3`; on Windows you may use `pip`). On macOS/Linux, **raw sockets** often require **sudo**.
3. **Run the script** (from the project root):
   ```bash
   sudo python3 scripts/icmp_challenge22.py
   ```
   The script sends **one** ICMP packet with Type=3, Code=1 to 127.0.0.1.
4. **Stop the capture** and **save** as **`static/pcaps/challenge_22.pcapng`**.

### What to check

- Filter by **`icmp`**. One packet has **Type: 3**, **Code: 1**. Submit **ICMP_3_1**.

### Note

If you cannot use sudo/scapy, create the pcap manually in Wireshark: **File → New** (or edit a capture), then add one packet with ICMP Type=3, Code=1 (e.g. via a hex editor or packet generator).

---

## Challenge 27 – ICMP Echo Identifier

**Flag (submission):** `ID_2048` (Identifier field in the first ICMP Echo Reply is 2048).


### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Install Scapy** if needed: `pip3 install scapy`. Run with **sudo** on macOS/Linux.
3. **Run the script** (from the project root):
   ```bash
   sudo python3 scripts/icmp_challenge23.py
   ```
   The script sends one ICMP Echo Request with **Identifier=2048** to 127.0.0.1; the OS usually replies with Echo Reply using the same Identifier.
4. **Stop the capture** and **save** as **`static/pcaps/challenge_23.pcapng`**.

### What to check

- Filter by **`icmp`**. Find the first **Echo (ping) reply** (type 0); in the ICMP header the **Identifier** field is **2048**. Submit **ID_2048**.

---

## Challenge 28 – Multiple ICMP Types

**Flag (submission):** `TYPE11` (the ICMP type that appears exactly 3 times is 11 — Time Exceeded).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Install Scapy** and run with **sudo** (from the project root):
   ```bash
   sudo python3 scripts/icmp_challenge24.py
   ```
   The script sends: 3× Type 11 (Time Exceeded), 2× Type 8 (Echo Request), 2× Type 0 (Echo Reply), 2× Type 3 (Dest Unreachable).
3. **Stop the capture** and **save** as **`static/pcaps/challenge_24.pcapng`**.

### What to check

- Filter by **`icmp`**. Count packets by **Type** (0, 3, 8, 11). Type **11** appears **3** times. Submit **TYPE11**.

---

## Challenge 29 – ICMP Type Message

**Flag (submission):** `ICMP_MSG` (ICMP Type values in packet order spell this word in ASCII: 73, 67, 77, 80, 95, 77, 83, 71).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Install Scapy** and run with **sudo** (from the project root):
   ```bash
   sudo python3 scripts/icmp_challenge25.py
   ```
   The script sends 8 ICMP packets whose **Type** field values are the ASCII codes for **I C M P _ M S G**.
3. **Stop the capture** and **save** as **`static/pcaps/challenge_25.pcapng`**.

### What to check

- Filter by **`icmp`**. Sort by time; for each packet in order, read the **Type** value. Convert each to a character (73→I, 67→C, 77→M, 80→P, 95→_, 77→M, 83→S, 71→G). Concatenate to get **ICMP_MSG**. Submit **ICMP_MSG**.

---

