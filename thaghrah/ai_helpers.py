"""Encoding, hints, and Wireshark filter helpers for AI-generated challenges."""
import base64
import binascii
import codecs


def ai_filter_for_protocol(protocol: str) -> str:
    p = (protocol or "").strip().upper()
    mapping = {
        "HTTP": "http",
        "TCP": "tcp",
        "DNS": "dns",
        "FTP": "ftp",
        "ICMP": "icmp",
        "SMTP": "smtp",
        "TLS": "tls",
        "FORENSICS": 'frame contains "part="',
    }
    return mapping.get(p, "tcp")


def build_ai_hint(protocol: str, fragmentation: bool, encoding: str) -> str:
    filt = ai_filter_for_protocol(protocol)
    steps = [f"1. In Wireshark, apply the filter `{filt}` and inspect suspicious packets/payload fields."]
    if fragmentation:
        steps.append("2. Find packets containing `part=1`, `part=2`, `part=3`, etc., and copy each `data=` fragment.")
        steps.append("3. Rebuild the value by joining fragments in ascending part order.")
        decode_step_index = 4
    else:
        steps.append('2. Locate the payload/header line that contains `FLAG = "..."` and copy only the value in quotes.')
        decode_step_index = 3
    if (encoding or "none").lower() != "none":
        steps.append(f"{decode_step_index}. Decode the extracted value using `{encoding}`.")
        steps.append(f"{decode_step_index + 1}. Submit only the final decoded plain value (no `FLAG =`, no quotes).")
    else:
        steps.append(f"{decode_step_index}. Submit only the final plain value (no `FLAG =`, no quotes).")
    return "\n".join(steps)


def requested_encoding_from_prompt(prompt: str):
    low = (prompt or "").lower()
    if "base64" in low:
        return "base64"
    if "rot13" in low:
        return "rot13"
    if "hex" in low or "hexadecimal" in low:
        return "hex"
    if "xor" in low:
        return "xor"
    if any(k in low for k in ("encoding", "encoded", "encrypt", "encrypted", "obfuscate", "obfuscated")):
        return "base64"
    return None


def requested_fragmentation_from_prompt(prompt: str):
    low = (prompt or "").lower()
    positive = (
        "fragment",
        "fragmentation",
        "fragmented",
        "split into parts",
        "split packet",
        "chunked",
        "chunks",
        "reassemble",
    )
    negative = (
        "no fragmentation",
        "without fragmentation",
        "not fragmented",
        "single packet",
        "one packet",
    )
    if any(k in low for k in negative):
        return False
    if any(k in low for k in positive):
        return True
    return None


def encode_with_encoding(value: str, encoding: str):
    value = (value or "").strip()
    enc = (encoding or "none").strip().lower()
    if not value or enc == "none":
        return value
    if enc == "base64":
        return base64.b64encode(value.encode("utf-8")).decode("utf-8")
    if enc == "hex":
        return value.encode("utf-8").hex()
    if enc == "rot13":
        return codecs.encode(value, "rot_13")
    return value


def decode_with_encoding(value: str, encoding: str):
    value = (value or "").strip()
    enc = (encoding or "none").strip().lower()
    if not value or enc == "none":
        return None
    try:
        if enc == "base64":
            padded = value + ("=" * ((4 - len(value) % 4) % 4))
            return base64.b64decode(padded.encode("utf-8"), validate=False).decode("utf-8", errors="strict").strip()
        if enc == "hex":
            return bytes.fromhex(value).decode("utf-8", errors="strict").strip()
        if enc == "rot13":
            return codecs.decode(value, "rot_13").strip()
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return None
    return None
