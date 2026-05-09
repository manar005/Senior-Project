"""
Generate TLS 1.2 handshake traffic for Challenge (TLS handshake; pcap suffix 32) (TLS version identification).

The challenge flag is TLSVER_3_3 (TLS 1.2 = 0x0303). This script forces TLS 1.2 on
both client and server so Wireshark shows the negotiated version clearly.

1. Writes cert/key to static/keys/challenge_31_cert.pem and challenge_31_key.pem
   (optional: solvers only need the pcap).
2. Starts tshark or tcpdump on loopback to write static/pcaps/challenge_31.pcapng,
   runs a short TLS session, then stops the capture.

Usage (from project root):
  python3 scripts/tls_challenge32.py

If neither tshark nor tcpdump is available, capture manually in Wireshark on
loopback while the script runs the TLS session (or run run_tls_session()).

Requires: OpenSSL (for key generation). Optional: tshark or tcpdump for capture.
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
KEY_FILE = os.path.join(KEY_DIR, "challenge_31_key.pem")
CERT_FILE = os.path.join(KEY_DIR, "challenge_31_cert.pem")
PCAP_PATH = os.path.join(PROJECT_ROOT, "static", "pcaps", "challenge_31.pcapng")

HOST = "127.0.0.1"
PORT = 8443


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
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname="localhost") as ssock:
                ssock.recv(64)
        print("TLS 1.2 session completed (cert verified).")
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
                "Capture has no packets (file too small). Open Wireshark on loopback, "
                "then run: python3 scripts/tls_challenge32.py "
                "(with no capture tools the script only runs TLS; save as challenge_31.pcapng).",
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
    """Wireshark capture engine; often captures loopback reliably on macOS."""
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
    """Return (tool_name, argv) for writing PCAP_PATH, or None."""
    # -a duration:8 lets the process exit cleanly with packets flushed (avoid empty pcap on SIGTERM).
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
