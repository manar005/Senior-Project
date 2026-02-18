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
