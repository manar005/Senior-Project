"""
Generate TLS 1.2 traffic for Challenge (TLS cipher; pcap suffix 33) (cipher suite in Server Hello).

The challenge flag is CIPHER_C02F (TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256).
Server and client are both restricted to ECDHE-RSA-AES128-GCM-SHA256 so Wireshark
shows 0xc02f in Server Hello.

Usage (from project root):
  python3 scripts/tls_challenge33.py

Requires: OpenSSL (for key generation). Optional: tshark / dumpcap / tcpdump.
"""
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import ssl
import socket

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
KEY_DIR = os.path.join(PROJECT_ROOT, "static", "keys")
KEY_FILE = os.path.join(KEY_DIR, "challenge_35_key.pem")
CERT_FILE = os.path.join(KEY_DIR, "challenge_35_cert.pem")
PCAP_PATH = os.path.join(PROJECT_ROOT, "static", "pcaps", "challenge_35.pcapng")

HOST = "127.0.0.1"
# Distinct from challenge 34 (8443)
PORT = 8444

# OpenSSL name for suite 0xC02F — must match challenges/tls/challenge_35.py flag CIPHER_C02F
CIPHER_NAME = "ECDHE-RSA-AES128-GCM-SHA256"


def loopback_iface():
    if platform.system() == "Darwin":
        return "lo0"
    return "lo"


def ensure_keys():
    os.makedirs(KEY_DIR, exist_ok=True)
    if os.path.isfile(KEY_FILE) and os.path.isfile(CERT_FILE):
        return
    print("Generating RSA key and self-signed cert with OpenSSL...")
    try:
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-keyout",
                KEY_FILE,
                "-out",
                CERT_FILE,
                "-days",
                "365",
                "-nodes",
                "-subj",
                "/CN=localhost",
            ],
            check=True,
            capture_output=True,
        )
        print(f"Wrote {KEY_FILE} and {CERT_FILE}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("OpenSSL key generation failed:", e, file=sys.stderr)
        sys.exit(1)


def run_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers(CIPHER_NAME)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    try:
        conn, _ = sock.accept()
        with context.wrap_socket(conn, server_side=True) as ssock:
            ssock.sendall(b"ok\n")
    finally:
        sock.close()


def run_client():
    time.sleep(0.4)
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=CERT_FILE)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers(CIPHER_NAME)
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname="localhost") as ssock:
                ssock.recv(64)
        print(f"TLS 1.2 session completed (cipher {CIPHER_NAME} / 0xC02F).")
    except Exception as e:
        print("Client error:", e, file=sys.stderr)
        raise


def run_tls_session():
    ensure_keys()
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    run_client()
    thread.join(timeout=3)


def main():
    os.makedirs(os.path.dirname(PCAP_PATH), exist_ok=True)
    iface = loopback_iface()
    cmd = capture_command(iface)
    if cmd:
        name, argv = cmd
        print(f"Capturing with {name} on {iface} → {PCAP_PATH} (8s window)")
        proc = subprocess.Popen(
            argv,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        time.sleep(1.0)
        try:
            run_tls_session()
        except Exception:
            proc.kill()
            raise
        if name == "tcpdump":
            proc.terminate()
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
        else:
            try:
                proc.wait(timeout=12)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
        err = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
        if err and "error" in err.lower() and "packets" not in err.lower():
            print(err[:400], file=sys.stderr)
        sz = os.path.getsize(PCAP_PATH) if os.path.isfile(PCAP_PATH) else 0
        if sz > 200:
            print(f"Saved {PCAP_PATH} ({sz} bytes)")
        else:
            print(
                "Capture has no packets (file too small). Capture on loopback in Wireshark, "
                "then run this script and save as static/pcaps/challenge_35.pcapng.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print("No tshark/dumpcap/tcpdump; running TLS session only (capture with Wireshark on loopback).")
        run_tls_session()
        print(f"Save your capture as {PCAP_PATH}")


def _wireshark_macos_bin(name):
    if platform.system() != "Darwin":
        return None
    p = os.path.join("/Applications/Wireshark.app/Contents/MacOS", name)
    return p if os.path.isfile(p) else None


def find_tshark():
    for tshark in (shutil.which("tshark"), _wireshark_macos_bin("tshark")):
        if not tshark:
            continue
        try:
            subprocess.run(
                [tshark, "-v"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return tshark
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    return None


def find_dumpcap():
    for dumpcap in (shutil.which("dumpcap"), _wireshark_macos_bin("dumpcap")):
        if not dumpcap:
            continue
        try:
            subprocess.run(
                [dumpcap, "-v"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return dumpcap
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    return None


def capture_command(iface):
    tshark = find_tshark()
    if tshark:
        return ("tshark", [tshark, "-i", iface, "-w", PCAP_PATH, "-a", "duration:8"])
    dumpcap = find_dumpcap()
    if dumpcap:
        return ("dumpcap", [dumpcap, "-i", iface, "-w", PCAP_PATH, "-a", "duration:8"])
    td = shutil.which("tcpdump")
    if td:
        return ("tcpdump", [td, "-i", iface, "-w", PCAP_PATH, "-U"])
    return None


if __name__ == "__main__":
    main()
