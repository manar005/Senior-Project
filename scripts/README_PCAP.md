# Creating pcap files for network challenges

Capture on **loopback** (e.g. `127.0.0.1` / Loopback adapter) unless noted. Save files under `static/pcaps/` as `challenge_XX.pcapng`.

---

## Challenge 4 – FTP Credential Extraction

**Flag (submission):** Base64 of `ADMIN_SECRET123` → `QURNSU5fU0VDUkVUMTIz`  
**In the capture:** Plaintext FTP login (USER ADMIN, PASS SECRET123).

### Steps

1. **Start Wireshark** and begin a capture on the loopback interface (e.g. **Loopback** or **Adapter for loopback traffic**).
2. **Run the script** (from the project root):
   ```bash
   python scripts/ftp_credentials_challenge04.py
   ```
   The script starts a minimal FTP server on `127.0.0.1:2121`, then an FTP client connects and logs in with **ADMIN** / **SECRET123**. The whole run is short (about a second).
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_04.pcapng`** (File → Save As…).

### What to check

- **Use filter `tcp.port == 2121`** (not `ftp`—Wireshark’s "ftp" only matches port 21; this script uses 2121).
- You should see TCP packets whose payload contains **USER ADMIN** and **PASS SECRET123** in plaintext.
- Solver flow: find credentials → form `ADMIN_SECRET123` → Base64‑encode → submit `QURNSU5fU0VDUkVUMTIz`.

### Port note

The script uses port **2121** so it does not require administrator/root. If something else uses 2121, change `PORT` in `scripts/ftp_credentials_challenge04.py`.

---

## Challenge 5 – ICMP Packet Analysis

**Flag (submission):** `ICMP_TYPE_8` (ICMP Echo Request type code).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface (e.g. **Loopback** or **Adapter for loopback traffic**).
2. **Run the script** (from the project root):
   ```bash
   python scripts/icmp_ping_challenge05.py
   ```
   The script sends one ping (ICMP Echo Request, type 8) to `127.0.0.1`.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_05.pcapng`** (File → Save As…).

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
   python scripts/smtp_protocol_challenge06.py
   ```
   The script starts a minimal SMTP server on `127.0.0.1:2525`, then a client connects and sends HELO and QUIT (SMTP dialog).
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_06.pcapng`** (File → Save As…).

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
   python scripts/tcp_handshakes_challenge07.py
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
   python scripts/tcp_fragmented_flag_challenge08.py
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
   python scripts/tcp_fragmented_image_challenge09.py
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

## Challenge 11 – HTTP Login Brute Force

**Flag (submission):** `p@ssw0rd!` (the correct password used in the successful login attempt).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/http_bruteforce_challenge11.py
   ```
   The script starts a simple HTTP server on `127.0.0.1:8081` with a `/login` endpoint, then a client sends several `POST /login` requests with different passwords for the **operator** user. Several attempts return `401 Invalid credentials.`; one attempt (the 5th) with the correct password returns `200 Login successful. Welcome, operator!` Two more failed attempts follow after the success.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_11.pcapng`** (File → Save As…).

### What to check

- Filter by **`tcp.port == 8081`** or **`http`**. Look for `POST /login` requests.
- Inspect the request bodies (e.g., using the **HTTP** tab or raw payload) to see the username and password fields, and compare them with the server responses.
- Most attempts get a `401` response with the body `"Invalid credentials."`. One attempt (in the middle of the sequence, with two more failed attempts after it) gets `200 OK` with `"Login successful. Welcome, operator!"`.
- The flag is the password value in that successful request, formatted exactly as seen: **`p@ssw0rd!`**.

---

## Challenge 12 – HTTP Status Code

**Flag (submission):** `STATUS_404` (find the response that returned HTTP 404 and submit in this format).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/http_status_challenge12.py
   ```
   The script starts an HTTP server on `127.0.0.1:8776`. A client requests `/`, `/about`, `/missing`, and `/index`. The server returns **200** for `/`, `/about`, and `/index`; it returns **404** for `/missing`.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_12.pcapng`** (File → Save As…).

### What to check

- Filter by **`http`** or **`tcp.port == 8776`**. Find the response to **GET /missing** (status 404). The flag **STATUS_404** appears in that response’s **X-Flag** header and in the response body. Submit **STATUS_404**.

---

## Challenge 13 – HTTP Request Method

**Flag (submission):** `METHOD_POST` (found in the response to the POST request).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/http_method_challenge13.py
   ```
   The script starts an HTTP server on `127.0.0.1:8777`. A client sends **GET /** and **GET /page**, then **POST /submit**. The response to **POST /submit** contains the flag **Base64-encoded** in the X-Flag header and body.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_13.pcapng`** (File → Save As…).

### What to check

- Filter by **`http`** or **`tcp.port == 8777`**. Find **POST /submit**, then **Follow → TCP Stream**. In the response you will see the encoded flag (Base64) in the X-Flag header and body. Decode it and submit **METHOD_POST**.

---

## Challenge 14 – HTTP Cookie Extraction

**Flag (submission):** `COOKIE_SESSION_FLAG` (the session cookie value from the Set-Cookie header after successful login).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/http_cookie_challenge14.py
   ```
   The script starts an HTTP server on `127.0.0.1:8778` with a `/login` endpoint. A client sends several `POST /login` requests with username **admin** and different passwords. Failed attempts return **401** with no Set-Cookie; the successful attempt (4th) returns **200** with **Set-Cookie: session=COOKIE_SESSION_FLAG; Path=/; HttpOnly**.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_14.pcapng`** (File → Save As…).

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
   python scripts/http_redirect_challenge15.py
   ```
   The script starts an HTTP server on `127.0.0.1:8779`. The client sends **separate connections** in this order: **GET /entry** (302 → /phase2), **GET /about** (200), **GET /phase2** (302 → /verify), **GET /help** (200), **GET /verify** (302 → /result), **GET /contact** (200), **GET /result** (200 with **X-Flag: REDIRECT_FINAL**). So /about and /help appear in between the redirect steps; the chain is spread across streams.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_15.pcapng`** (File → Save As…).

### What to check

- Filter by **`http`** or **`tcp.port == 8779`**. Each request is a separate TCP stream. Find streams with **302** responses; the chain is interleaved with **GET /about**, **GET /help**, **GET /contact** (all 200). Follow **Location** from one stream to the next: /entry → /phase2 → /verify → /result. The stream with **GET /result** and **200 OK** contains **X-Flag: REDIRECT_FINAL**. Submit **REDIRECT_FINAL**.

---

## Challenge 17 – Port-Knock Flag

**Flag (submission):** `KNOCK_OPEN` (destination ports of the SYN packets, in order, spell the flag as ASCII).

### Steps

1. **Start Wireshark** and begin a capture on the **loopback** interface.
2. **Run the script** (from the project root):
   ```bash
   python scripts/port_knock_challenge17.py
   ```
   The script tries to connect to **127.0.0.1** on a sequence of ports (75, 78, 79, 67, 75, 95, 79, 80, 69, 78). No server is listening, so each attempt sends a **TCP SYN** and then gets RST or times out. The **destination port** of each SYN, in packet order, is the ASCII code for **K N O C K _ O P E N**.
3. **Stop the capture** in Wireshark.
4. **Save** the capture as **`static/pcaps/challenge_17.pcapng`** (File → Save As…).

### What to check

- Filter for initial SYNs: **`tcp.flags.syn==1 and tcp.flags.ack==0`**. For each packet, note the **Destination port** in the TCP header (75, 78, 79, 67, 75, 95, 79, 80, 69, 78). Convert each to ASCII (e.g. 75 = K, 78 = N, …) and concatenate to get **KNOCK_OPEN**.
- Solver submits **KNOCK_OPEN**.

