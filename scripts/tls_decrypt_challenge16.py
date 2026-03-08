"""
Generate TLS traffic and private key for Challenge 16 (TLS Decryption).

1. Generates a self-signed cert and private key.
2. Writes the private key to static/keys/challenge_16_private.pem (for solvers to download).
3. Starts a TLS server on 127.0.0.1:9443 that sends the flag when a client connects.
4. Connects as a client to generate traffic (or you can run: openssl s_client -connect 127.0.0.1:9443).

To capture the pcap:
  - Start Wireshark, capture on loopback (lo0 or lo), then run this script.
  - Save the capture as static/pcaps/challenge_16.pcapng.
  - Or: tshark -i lo0 -w static/pcaps/challenge_16.pcapng -a duration:8 &
    Then run: python scripts/tls_decrypt_challenge16.py
    (Stop tshark after the script finishes if needed.)

Requires: OpenSSL installed (for key generation). Python 3 ssl/stdlib only for server/client.
"""
import os
import sys
import ssl
import socket
import threading
import time
import subprocess

# Must match challenges/tls/challenge_16.py
FLAG_MESSAGE = "FLAG: TLS_DECRYPT_16\n"
HOST = "127.0.0.1"
PORT = 9443

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
KEY_DIR = os.path.join(PROJECT_ROOT, "static", "keys")
KEY_FILE = os.path.join(KEY_DIR, "challenge_16_private.pem")
CERT_FILE = os.path.join(KEY_DIR, "challenge_16_cert.pem")
PCAP_PATH = os.path.join(PROJECT_ROOT, "static", "pcaps", "challenge_16.pcapng")


def ensure_keys():
    """Generate key and cert with OpenSSL if key file does not exist."""
    os.makedirs(KEY_DIR, exist_ok=True)
    if os.path.isfile(KEY_FILE):
        print(f"Using existing key: {KEY_FILE}")
        return
    print("Generating RSA key and self-signed cert with OpenSSL...")
    try:
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", KEY_FILE, "-out", CERT_FILE,
            "-days", "365", "-nodes",
            "-subj", "/CN=localhost"
        ], check=True, capture_output=True)
        print(f"Wrote {KEY_FILE} and {CERT_FILE}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("OpenSSL key generation failed:", e, file=sys.stderr)
        print("Install OpenSSL or create key/cert manually.", file=sys.stderr)
        sys.exit(1)


def run_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)
    # Force TLS 1.2 so Wireshark can decrypt with the server's RSA key (TLS 1.3 doesn't use RSA key exchange)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    # Force RSA key exchange (no DHE/ECDHE) so the server's private key can decrypt the session in Wireshark
    context.set_ciphers('AES128-SHA:AES256-SHA')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    try:
        conn, _ = sock.accept()
        with context.wrap_socket(conn, server_side=True) as ssock:
            ssock.sendall(FLAG_MESSAGE.encode("utf-8"))
    finally:
        sock.close()


def run_client():
    time.sleep(0.5)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Force TLS 1.2 to match server (so capture decrypts in Wireshark with RSA key)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    # Same RSA-only ciphers so key exchange uses server's RSA key (decryptable in Wireshark)
    context.set_ciphers('AES128-SHA:AES256-SHA')
    try:
        with socket.create_connection((HOST, PORT), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname="localhost") as ssock:
                data = ssock.recv(256).decode("utf-8")
                if "TLS_DECRYPT_16" in data:
                    print("Client received flag from server (TLS OK).")
    except Exception as e:
        print("Client connect:", e)


def main():
    ensure_keys()
    print(f"Start Wireshark capture on loopback, then connect to {HOST}:{PORT}")
    print("Server will send the flag once and exit.")
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    run_client()
    time.sleep(0.2)


if __name__ == "__main__":
    main()
