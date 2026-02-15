# How to Create the pcap File for Challenge 1

This guide walks you through creating a pcap that contains HTTP traffic with the flag `NETWORK_HTTP_FLAG_2026` in an HTTP response header.

---

## Option A: Live capture (recommended)

You run a tiny HTTP server that sends the flag in a header, then capture the traffic with Wireshark.

### Step 1: Create a one-off HTTP server script

Create a script that listens on a port and responds with the flag in a custom header (e.g. `X-Flag`). Example using Python 3:

**File: `scripts/flag_server_challenge01.py`** (see below)

### Step 2: Start Wireshark and begin capturing

1. Open **Wireshark**.
2. Select the interface used for **localhost** traffic:
   - Windows: often **Loopback: lo** or **Npcap Loopback Adapter**
   - macOS: **lo0**
   - Linux: **lo**
3. If you don’t see loopback, install **Npcap** (Windows) with “Loopback” support enabled.
4. Click the shark fin (Start capturing packets).

### Step 3: Start the flag server

In a terminal:

```bash
cd "c:\Users\ahmed\Desktop\Senior Project\Senior-Project"
python scripts/flag_server_challenge01.py
```

Leave it running. It will listen on `http://127.0.0.1:8765`.

### Step 4: Generate HTTP traffic

In **another** terminal:

```bash
curl http://127.0.0.1:8765/
```

Or open in a browser: `http://127.0.0.1:8765/`

You should see a short response; the important part is the header `X-Flag: NETWORK_HTTP_FLAG_2026`.

### Step 5: Stop the capture and save

1. In Wireshark, click the red square (Stop capturing).
2. In the filter bar type: `http` and press Enter so only HTTP packets are shown.
3. **File → Save As…**
4. Save as e.g. `challenge_01.pcap` (or `challenge_01.pcapng`).
5. Recommended: put the file in your project, e.g. `static/pcaps/challenge_01.pcap`.

### Step 6: Verify the pcap

1. Open the saved pcap in Wireshark.
2. Filter: `http`.
3. Select an HTTP response (e.g. “200 OK”).
4. In the packet details, expand **Hypertext Transfer Protocol** and look for the header containing `NETWORK_HTTP_FLAG_2026` (e.g. `X-Flag`).

### Step 7: Use the pcap in the app

- Place `challenge_01.pcap` where your app serves it (e.g. `static/pcaps/`).
- Add a “Download pcap” link on the Challenge 1 page that points to this file.

---

## Option B: Capture with tshark (command-line)

If you prefer the command line:

1. Start the flag server (Step 3 above).
2. In an **elevated** or allowed terminal, start capture on loopback (replace `Loopback` with your loopback interface name if different):

   **Windows (PowerShell as Admin):**
   ```bash
   & "C:\Program Files\Wireshark\tshark.exe" -i "\Device\NPF_Loopback" -w challenge_01.pcap
   ```

   **Linux/macOS:**
   ```bash
   tshark -i lo -w challenge_01.pcap
   ```

3. In another terminal: `curl http://127.0.0.1:8765/`
4. Stop tshark (Ctrl+C).
5. Use the saved `challenge_01.pcap` as in Step 6–7 above.

---

## Troubleshooting

- **No loopback interface**: Install Npcap (Windows) with “Support loopback traffic” checked.
- **No HTTP in capture**: Ensure you capture on the same machine where the server runs (127.0.0.1) and that you use the loopback interface.
- **Only one packet**: Run `curl` or open the URL in the browser after capture has started; you should see at least TCP handshake, HTTP request, and HTTP response.

Once the pcap is created and linked from the challenge page, users can download it and find the flag in the HTTP response headers as described in the challenge.
