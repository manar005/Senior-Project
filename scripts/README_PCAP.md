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
