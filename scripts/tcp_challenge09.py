"""
One-off script for Challenge 9 pcap. Sends a single image (PNG) over one TCP connection
to 127.0.0.1:9998. The image displays the flag (IMAGE_FLAG_9). Solver follows the
TCP stream, saves the raw payload as .png, and opens it to see the flag.

Run while capturing on loopback in Wireshark; save as static/pcaps/challenge_09.pcapng.
Requires: pip install Pillow
"""
import io
import socket
import threading
import time

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Install Pillow: pip install Pillow")

HOST = "127.0.0.1"
PORT = 9998
FLAG_TEXT = "IMAGE_FLAG_9"


def make_flag_image():
    """Create a small PNG image that displays the flag text. Returns PNG bytes."""
    w, h = 320, 80
    img = Image.new("RGB", (w, h), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except OSError:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except OSError:
            font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), FLAG_TEXT, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (w - tw) // 2
    y = (h - th) // 2
    draw.text((x, y), FLAG_TEXT, fill="black", font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def run_server(png_bytes):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    try:
        conn, _ = sock.accept()
        conn.sendall(png_bytes)
        conn.close()
    finally:
        sock.close()


def main():
    png_bytes = make_flag_image()
    server_thread = threading.Thread(target=run_server, args=(png_bytes,), daemon=True)
    server_thread.start()
    time.sleep(0.3)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((HOST, PORT))
        data = b""
        while True:
            part = s.recv(4096)
            if not part:
                break
            data += part
        s.close()
    except (socket.timeout, socket.error, OSError):
        pass
    time.sleep(0.1)


if __name__ == "__main__":
    main()
