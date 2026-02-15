# How to Create the pcap File for Challenge 3

Challenge 3 asks users to find the **domain name** in a DNS query and submit it as UPPERCASE with underscores (e.g. **dns.query.flag** → **DNS_QUERY_FLAG**). The pcap must contain a DNS query for **dns.query.flag**.

---

## Step 1: Start Wireshark

1. Open **Wireshark**.
2. Select the interface that carries your **DNS traffic**:
   - Usually your **Wi‑Fi** or **Ethernet** adapter (DNS goes to your router/ISP).
   - Do **not** use loopback unless you have a local DNS server on 127.0.0.1.
3. Click the blue shark fin to **start capturing**.

---

## Step 2: Generate a DNS query for dns.query.flag

In a terminal, from the project folder:

```bash
python scripts/dns_query_challenge03.py
```

This triggers a DNS lookup for **dns.query.flag**. The query will appear in Wireshark even if the domain doesn’t resolve (you may see an error in the script; that’s fine).

**Alternative (no script):** If you have `nslookup` or `dig`:

```bash
nslookup dns.query.flag
```

or

```bash
dig dns.query.flag
```

---

## Step 3: Stop the capture and save

1. In Wireshark, click the red square to **stop** the capture.
2. In the filter bar type: **`dns`** and press Enter.
3. Find a packet that shows **dns.query.flag** in the DNS Queries section.
4. **File → Save As…**
5. Save as **`challenge_03.pcapng`** (or `challenge_03.pcap`).
6. Put the file in **`static/pcaps/challenge_03.pcapng`**.

---

## Step 4: Verify the pcap

1. Open the saved file in Wireshark.
2. Filter: **`dns`**.
3. Select a DNS query packet.
4. In the packet details, expand **Domain Name System (query)** → **Queries**.
5. Confirm the **Name** field is **dns.query.flag**.

---

## Step 5: Use it in the app

- Place the file at **`static/pcaps/challenge_03.pcapng`**.
- The Challenge 3 page has a “Download pcap” link pointing to this file.

---

## Troubleshooting

- **No DNS packets:** Make sure you started the capture *before* running the script. Run the script again while capturing.
- **DNS on loopback:** If you use a local DNS proxy (e.g. on 127.0.0.1), capture on the loopback interface and run the script; the query will appear there.
