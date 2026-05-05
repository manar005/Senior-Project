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
        if (encoding or "").lower() == "xor":
            steps.append(
                f"{decode_step_index}. Locate the XOR key in the packet data (look for `XOR_KEY=...`), "
                "then decrypt the extracted value using that key."
            )
            steps.append(
                f"{decode_step_index + 1}. In CyberChef (https://gchq.github.io/CyberChef/): paste the extracted value, "
                "add `From Hex`, then add `XOR`."
            )
            steps.append(
                f"{decode_step_index + 2}. In the XOR operation, set the key to the packet key value "
                "(for example `23`) and set the key format to Decimal."
            )
            steps.append(
                f"{decode_step_index + 3}. Submit only the decrypted plain value (no `FLAG =`, no quotes)."
            )
        else:
            steps.append(f"{decode_step_index}. Decode the extracted value using `{encoding}`.")
            steps.append(f"{decode_step_index + 1}. Submit only the final decoded plain value (no `FLAG =`, no quotes).")
    else:
        steps.append(f"{decode_step_index}. Submit only the final plain value (no `FLAG =`, no quotes).")
    return "\n".join(steps)


def requested_encoding_from_prompt(prompt: str):
    low = (prompt or "").lower()
    negative = (
        "no encoding",
        "without encoding",
        "not encoded",
        "plain flag",
        "plaintext",
        "plain text",
        "no encryption",
        "without encryption",
        "not encrypted",
    )
    if any(k in low for k in negative):
        return None
    if "base64" in low:
        return "base64"
    if "rot13" in low:
        return "rot13"
    if "hex" in low or "hexadecimal" in low:
        return "hex"
    if "xor" in low:
        return "xor"
    # Explicitly treat "encoding/encoded" as a request for encoded on-wire flag.
    # Do not infer encoding from "encryption/encrypted" wording.
    if any(k in low for k in ("encoding", "encoded", "obfuscate", "obfuscated")):
        return "base64"
    return None


def requested_encryption_from_prompt(prompt: str) -> bool:
    """True when the user explicitly asks for encryption semantics."""
    low = (prompt or "").lower()
    return any(k in low for k in ("encrypt", "encrypted", "encryption", "decrypt", "decryption", "cipher"))


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
    if enc == "xor":
        # Deterministic single-byte XOR then hex-encode for packet-safe text.
        key = 23
        raw = bytes((b ^ key) for b in value.encode("utf-8"))
        return raw.hex()
    if enc == "custom":
        # Keep "custom" predictable and reversible.
        return value[::-1]
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
        if enc == "xor":
            key = 23
            raw = bytes.fromhex(value)
            decoded = bytes((b ^ key) for b in raw)
            return decoded.decode("utf-8", errors="strict").strip()
        if enc == "custom":
            return value[::-1].strip()
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return None
    return None
