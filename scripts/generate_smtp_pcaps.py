"""
Generate pcaps for SMTP challenges 6 and 30–33 on 127.0.0.1:2525.

Run from project root:
  python3 scripts/generate_smtp_pcaps.py           # all
  python3 scripts/generate_smtp_pcaps.py 30 31   # subset

Requires: tshark or dumpcap or tcpdump (Wireshark on macOS). OpenSSL not required.

Challenge flags must match the traffic (see challenges/smtp/challenge_*.py).
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import socket

HOST = "127.0.0.1"
PORT = 2525

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PCAP_DIR = os.path.join(PROJECT_ROOT, "static", "pcaps")


def pcap_path(n: int) -> str:
    return os.path.join(PCAP_DIR, f"challenge_{n:02d}.pcapng")


def loopback_iface():
    return "lo0" if platform.system() == "Darwin" else "lo"


def _wireshark_macos_bin(name: str) -> str | None:
    if platform.system() != "Darwin":
        return None
    p = os.path.join("/Applications/Wireshark.app/Contents/MacOS", name)
    return p if os.path.isfile(p) else None


def find_tshark() -> str | None:
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


def find_dumpcap() -> str | None:
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


def capture_command(iface: str, out_path: str) -> tuple[str, list[str]] | None:
    tshark = find_tshark()
    if tshark:
        return ("tshark", [tshark, "-i", iface, "-w", out_path, "-a", "duration:8"])
    dumpcap = find_dumpcap()
    if dumpcap:
        return ("dumpcap", [dumpcap, "-i", iface, "-w", out_path, "-a", "duration:8"])
    td = shutil.which("tcpdump")
    if td:
        return ("tcpdump", [td, "-i", iface, "-w", out_path, "-U"])
    return None


def run_with_capture(challenge_num: int, session_fn) -> None:
    os.makedirs(PCAP_DIR, exist_ok=True)
    path = pcap_path(challenge_num)
    iface = loopback_iface()
    cmd = capture_command(iface, path)
    if not cmd:
        print("No capture tool; run session only. Save manually as", path, file=sys.stderr)
        session_fn()
        return
    name, argv = cmd
    print(f"[ch {challenge_num}] {name} → {path}")
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    time.sleep(1.0)
    try:
        session_fn()
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
    sz = os.path.getsize(path) if os.path.isfile(path) else 0
    if sz < 200:
        print(f"[ch {challenge_num}] WARNING: capture very small ({sz} bytes)", file=sys.stderr)
    else:
        print(f"[ch {challenge_num}] OK ({sz} bytes)")


# --- SMTP line helpers ---

def _readline(conn: socket.socket, buf: bytearray) -> str:
    while b"\r\n" not in buf:
        chunk = conn.recv(4096)
        if not chunk:
            break
        buf.extend(chunk)
    if b"\r\n" not in buf:
        return ""
    i = buf.index(b"\r\n")
    line = bytes(buf[:i]).decode("utf-8", errors="replace").strip()
    del buf[: i + 2]
    return line


def _send(conn: socket.socket, data: bytes) -> None:
    conn.sendall(data)


# --- Scenario 6 (same as smtp_protocol_challenge06.py) ---

def session_06():
    def server():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(1)
        try:
            conn, _ = sock.accept()
            conn.sendall(b"220 localhost ESMTP Challenge 6\r\nProtocol: SMTP\r\n")
            while True:
                data = conn.recv(1024).decode("utf-8", errors="ignore")
                if not data:
                    break
                line = data.strip().upper()
                if line.startswith("HELO") or line.startswith("EHLO"):
                    conn.sendall(b"250 Hello\r\n")
                elif line.startswith("QUIT"):
                    conn.sendall(b"221 Bye\r\n")
                    break
                else:
                    conn.sendall(b"250 OK\r\n")
            conn.close()
        finally:
            sock.close()

    t = threading.Thread(target=server, daemon=True)
    t.start()
    time.sleep(0.35)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((HOST, PORT))
        s.recv(2048)
        s.sendall(b"HELO client\r\n")
        s.recv(1024)
        s.sendall(b"QUIT\r\n")
        s.recv(1024)
        s.close()
    except OSError:
        pass
    time.sleep(0.25)
    t.join(timeout=2)


# --- Challenge 30: second command MAIL FROM:<sender@challenge.lab> ---

def session_30():
    def server():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(1)
        try:
            conn, _ = sock.accept()
            buf = bytearray()
            _send(conn, b"220 smtp.lab ESMTP ready\r\n")
            while True:
                line = _readline(conn, buf).upper()
                if not line:
                    break
                if line.startswith("EHLO") or line.startswith("HELO"):
                    _send(conn, b"250 lab greets you\r\n")
                elif line.startswith("MAIL FROM"):
                    _send(conn, b"250 2.1.0 Ok\r\n")
                elif line.startswith("QUIT"):
                    _send(conn, b"221 bye\r\n")
                    break
                else:
                    _send(conn, b"502 command not implemented\r\n")
            conn.close()
        finally:
            sock.close()

    t = threading.Thread(target=server, daemon=True)
    t.start()
    time.sleep(0.35)
    try:
        c = socket.create_connection((HOST, PORT), timeout=3)
        c.recv(2048)
        c.sendall(b"EHLO student.client\r\n")
        c.recv(1024)
        c.sendall(b"MAIL FROM:<sender@challenge.lab>\r\n")
        c.recv(1024)
        c.sendall(b"QUIT\r\n")
        c.recv(1024)
        c.close()
    except OSError as e:
        print("client 30:", e, file=sys.stderr)
    time.sleep(0.25)
    t.join(timeout=2)


# --- Challenges 31, 32, 33: full DATA flow (server replies 220,250,250,250,354,250,221) ---

def _smtp_server_full_mail(data_lines: bytes):
    def server():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(1)
        try:
            conn, _ = sock.accept()
            buf = bytearray()
            _send(conn, b"220 smtp.challenge ESMTP\r\n")
            line = _readline(conn, buf).upper()
            if line.startswith("EHLO") or line.startswith("HELO"):
                _send(conn, b"250 Hello\r\n")
            line = _readline(conn, buf).upper()
            if line.startswith("MAIL FROM"):
                _send(conn, b"250 2.1.0 Ok\r\n")
            line = _readline(conn, buf).upper()
            if line.startswith("RCPT TO"):
                _send(conn, b"250 2.1.5 Ok\r\n")
            line = _readline(conn, buf).upper()
            if line.startswith("DATA"):
                _send(conn, b"354 End data with <CR><LF>.<CR><LF>\r\n")
            body_buf = bytearray(buf)
            buf.clear()
            while True:
                while b"\r\n" not in body_buf and len(body_buf) < 65536:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    body_buf.extend(chunk)
                if b"\r\n" not in body_buf:
                    break
                i = body_buf.index(b"\r\n")
                line_b = bytes(body_buf[:i])
                del body_buf[: i + 2]
                if line_b == b".":
                    break
            _send(conn, b"250 2.0.0 Message accepted\r\n")
            if body_buf:
                buf[:] = body_buf
            line = _readline(conn, buf)
            if line.upper().startswith("QUIT"):
                _send(conn, b"221 bye\r\n")
            conn.close()
        finally:
            sock.close()

    def client(body: bytes):
        time.sleep(0.35)
        c = socket.create_connection((HOST, PORT), timeout=5)
        c.recv(2048)
        c.sendall(b"EHLO lab.client\r\n")
        c.recv(1024)
        c.sendall(b"MAIL FROM:<from@lab.local>\r\n")
        c.recv(1024)
        c.sendall(b"RCPT TO:<to@lab.local>\r\n")
        c.recv(1024)
        c.sendall(b"DATA\r\n")
        c.recv(1024)
        c.sendall(body + b"\r\n.\r\n")
        c.recv(1024)
        c.sendall(b"QUIT\r\n")
        c.recv(1024)
        c.close()

    t = threading.Thread(target=server, daemon=True)
    t.start()
    try:
        client(data_lines)
    except OSError as e:
        print("client mail:", e, file=sys.stderr)
    time.sleep(0.25)
    t.join(timeout=3)


def session_31():
    _smtp_server_full_mail(b"Subject: test\r\n\r\nminimal body.\r\n")


def session_32():
    body = (
        b"From: student@lab.local\r\n"
        b"To: grader@lab.local\r\n"
        b"X-Flag: SMTP_HEADER_FLAG\r\n"
        b"Subject: challenge\r\n"
        b"\r\n"
        b"Body text.\r\n"
    )
    _smtp_server_full_mail(body)


def session_33():
    session_31()


ALL_SESSIONS = {
    6: session_06,
    30: session_30,
    31: session_31,
    32: session_32,
    33: session_33,
}


def main():
    args = [int(a) for a in sys.argv[1:] if a.isdigit()]
    targets = args if args else [6, 30, 31, 32, 33]
    for n in targets:
        if n not in ALL_SESSIONS:
            print("Unknown challenge:", n, file=sys.stderr)
            continue
        run_with_capture(n, ALL_SESSIONS[n])
        time.sleep(0.5)


if __name__ == "__main__":
    main()
