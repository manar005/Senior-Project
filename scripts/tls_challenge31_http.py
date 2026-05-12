"""
Generate HTTP-over-TLS traffic for Challenge 31 (pcap suffix 31).

TLS 1.2 with RSA key exchange (AES128-SHA / AES256-SHA) so Wireshark can decrypt
using RSA keys list. After the handshake, the client sends a minimal HTTP request
and the server replies with HTTP/1.1 including X-Flag (flag is in the header, not raw blob).

Keys: static/keys/challenge_31_key.pem + challenge_31_cert.pem (same as challenge page download aliases).

Usage (from project root):
  python3 scripts/tls_challenge31_http.py

Requires: OpenSSL if keys missing; tshark/dumpcap/tcpdump optional for automatic capture.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import ssl
import socket

# Must match challenges/tls/challenge_31.py
FLAG = "HTTP_TLS_FLAG"

HOST = "127.0.0.1"
PORT = 9443

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
KEY_DIR = os.path.join(PROJECT_ROOT, "static", "keys")
KEY_FILE = os.path.join(KEY_DIR, "challenge_31_key.pem")
CERT_FILE = os.path.join(KEY_DIR, "challenge_31_cert.pem")
PRIVATE_ALIAS = os.path.join(KEY_DIR, "challenge_31_private.pem")
PCAP_PATH = os.path.join(PROJECT_ROOT, "static", "pcaps", "challenge_31.pcapng")

HTTP_RESPONSE = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/plain\r\n"
    f"X-Flag: {FLAG}\r\n"
    "Content-Length: 0\r\n"
    "\r\n"
)


def loopback_iface():
    return "lo0" if platform.system() == "Darwin" else "lo"


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


def sync_private_alias():
    """challenge.html links to challenge_31_private.pem"""
    try:
        if os.path.isfile(KEY_FILE):
            shutil.copyfile(KEY_FILE, PRIVATE_ALIAS)
    except OSError:
        pass


def run_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers("AES128-SHA:AES256-SHA")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    try:
        conn, _ = sock.accept()
        with context.wrap_socket(conn, server_side=True) as ssock:
            buf = b""
            while b"\r\n\r\n" not in buf and len(buf) < 16384:
                chunk = ssock.recv(4096)
                if not chunk:
                    break
                buf += chunk
            ssock.sendall(HTTP_RESPONSE.encode("utf-8"))
    finally:
        sock.close()


def run_client():
    time.sleep(0.5)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers("AES128-SHA:AES256-SHA")
    req = b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname="localhost") as ssock:
                ssock.sendall(req)
                data = ssock.recv(4096).decode("utf-8", errors="replace")
                if FLAG in data:
                    print("Client received HTTP response with X-Flag (OK).")
    except Exception as e:
        print("Client error:", e, file=sys.stderr)
        raise


def run_tls_session():
    ensure_keys()
    sync_private_alias()
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    run_client()
    thread.join(timeout=5)


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
            subprocess.run([tshark, "-v"], capture_output=True, check=True, timeout=5)
            return tshark
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    return None


def find_dumpcap():
    for dumpcap in (shutil.which("dumpcap"), _wireshark_macos_bin("dumpcap")):
        if not dumpcap:
            continue
        try:
            subprocess.run([dumpcap, "-v"], capture_output=True, check=True, timeout=5)
            return dumpcap
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    return None


def capture_filter():
    """BPF: only our TLS session (avoids unrelated lo0 noise like mDNS)."""
    return f"host {HOST} and tcp port {PORT}"


def capture_command(iface):
    bpf = capture_filter()
    dur = "12"
    tshark = find_tshark()
    if tshark:
        return (
            "tshark",
            [tshark, "-i", iface, "-f", bpf, "-w", PCAP_PATH, "-a", f"duration:{dur}"],
        )
    dumpcap = find_dumpcap()
    if dumpcap:
        return (
            "dumpcap",
            [dumpcap, "-i", iface, "-f", bpf, "-w", PCAP_PATH, "-a", f"duration:{dur}"],
        )
    td = shutil.which("tcpdump")
    if td:
        return (
            "tcpdump",
            [td, "-i", iface, "-s", "0", "-w", PCAP_PATH, "-U", bpf],
        )
    return None


def pcap_has_tls_handshake():
    tshark = find_tshark()
    if not tshark or not os.path.isfile(PCAP_PATH):
        return False
    try:
        r = subprocess.run(
            [
                tshark,
                "-r",
                PCAP_PATH,
                "-Y",
                "tls.handshake.type == 1",
                "-T",
                "fields",
                "-e",
                "frame.number",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        lines = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
        return len(lines) > 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def main():
    os.makedirs(os.path.dirname(PCAP_PATH), exist_ok=True)
    iface = loopback_iface()
    cmd = capture_command(iface)
    if cmd:
        name, argv = cmd
        bpf = capture_filter()
        print(f"[challenge 31 HTTP/TLS] {name} on {iface} filter '{bpf}' → {PCAP_PATH}")
        proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        # Let capture attach before generating traffic (avoids empty / wrong pcaps).
        time.sleep(2.5)
        try:
            run_tls_session()
        except Exception:
            proc.kill()
            raise
        if name == "tcpdump":
            time.sleep(2.0)
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
        else:
            try:
                proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
        err = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
        if err.strip():
            print(err.strip()[:800], file=sys.stderr)
        sz = os.path.getsize(PCAP_PATH) if os.path.isfile(PCAP_PATH) else 0
        if sz < 200 or not pcap_has_tls_handshake():
            print(
                "Capture missing TLS (no Client Hello). Expected TCP to 127.0.0.1:9443 on "
                f"loopback. Re-run this script with tshark/dumpcap available, or capture lo0 "
                f"manually with filter '{bpf}' while this script runs. "
                f"Got file size={sz} bytes.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Saved {PCAP_PATH} ({sz} bytes); TLS Client Hello present.")
    else:
        print("No tshark/dumpcap/tcpdump; running session only.")
        run_tls_session()
        print(f"Save capture as {PCAP_PATH}")


if __name__ == "__main__":
    main()
