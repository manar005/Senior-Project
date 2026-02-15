# How to Create the pcap File for Challenge 2

Challenge 2 asks users to find the **TCP destination port** in a handshake and submit it in hex (e.g. **PORT_0x1F90**). Port **8080** in hex is **0x1F90**, so the pcap must show a TCP connection to port **8080**.

---

## Step 1: Start Wireshark and choose loopback

1. Open **Wireshark**.
2. Select the **loopback** interface:
   - **Windows:** e.g. "Loopback" or "Npcap Loopback Adapter"
   - **macOS:** **lo0**
   - **Linux:** **lo**
3. If you don’t see loopback, install **Npcap** (Windows) with “Support loopback traffic” enabled.
4. Click the blue shark fin to **start capturing**.

---

## Step 2: Start the server on port 8080

In a terminal, from the project folder:

```bash
python scripts/port_server_challenge02.py
```

Leave it running. It listens on **http://127.0.0.1:8080/**.

---

## Step 3: Generate TCP traffic to port 8080

In **another** terminal (or in a browser):

```bash
curl http://127.0.0.1:8080/
```

Or open in a browser: **http://127.0.0.1:8080/**

One request is enough. You should see a TCP three-way handshake (SYN, SYN-ACK, ACK) to destination port **8080**.

---

## Step 4: Stop the capture and save

1. In Wireshark, click the red square to **stop** the capture.
2. In the filter bar type: **`tcp`** (or **`tcp.dstport == 8080`**) and press Enter.
3. Confirm you see packets with **Destination port: 8080** in the TCP header.
4. **File → Save As…**
5. Save as **`challenge_02.pcapng`** (or `challenge_02.pcap`).
6. Put the file in **`static/pcaps/challenge_02.pcapng`** so the app can serve it.

---

## Step 5: Verify the pcap

1. Open the saved file in Wireshark.
2. Filter: **`tcp`**.
3. Select a TCP packet (e.g. the SYN).
4. In the packet details, expand **Transmission Control Protocol** and check:
   - **Destination Port: 8080** (or 8080 in the “Dest port” column).
5. Optional: confirm 8080 in decimal = **0x1F90** in hex (correct flag: **PORT_0x1F90**).

---

## Step 6: Use it in the app

- Ensure the file is at **`static/pcaps/challenge_02.pcapng`**.
- The Challenge 2 page should have a “Download pcap” link pointing to this file (add it in the template if needed).

---

## Troubleshooting

- **“Address already in use”:** Something else is using port 8080. Stop that process or change `PORT` in `port_server_challenge02.py` and the challenge flag (port 8080 → 0x1F90 is required for the current flag).
- **No loopback in Wireshark:** Install/repair Npcap with loopback support, then restart Wireshark.
- **No TCP to 8080:** Make sure you use **127.0.0.1:8080** and that the server is running before you run `curl` or open the URL.
