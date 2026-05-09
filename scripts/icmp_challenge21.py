"""
One-off script for Challenge 5 pcap. Sends one ICMP Echo Request (type 8) to 127.0.0.1.
Flag = ICMP_TYPE_8. Run while capturing on loopback in Wireshark; save as
static/pcaps/challenge_21.pcapng.
"""
import platform
import subprocess
import sys

TARGET = "127.0.0.1"

def main():
    if platform.system() == "Windows":
        subprocess.run(
            ["ping", "-n", "1", TARGET],
            capture_output=True,
            timeout=5,
        )
    else:
        subprocess.run(
            ["ping", "-c", "1", TARGET],
            capture_output=True,
            timeout=5,
        )


if __name__ == "__main__":
    try:
        main()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Note: {e}", file=sys.stderr)
        sys.exit(1)
