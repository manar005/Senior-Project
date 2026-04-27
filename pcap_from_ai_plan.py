"""Build Wireshark-friendly PCAP from Grok pcap_plan using Scapy; optionally rewrite with tshark."""
import ipaddress
import os
import random
import re

# Scapy writes under XDG_CACHE_HOME; use a project-local cache so restricted home dirs still work.
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
_scapy_xdg = os.path.join(_pkg_dir, ".scapy_xdg_cache")
os.makedirs(_scapy_xdg, mode=0o700, exist_ok=True)
os.environ["XDG_CACHE_HOME"] = _scapy_xdg
import secrets
import shutil
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Optional

from ai_challenge_utils import canonical_flag_line, coerce_fragment_count, extract_flag_inner_value, parse_bool

try:
    from scapy.all import ICMP, IP, Raw, TCP, UDP, wrpcap  # type: ignore
except ImportError:
    IP = TCP = UDP = ICMP = Raw = wrpcap = None  # type: ignore


def _safe_ip(s: str) -> str:
    try:
        ipaddress.ip_address(s)
        return s
    except ValueError:
        return f"10.{random.randint(0, 250)}.{random.randint(0, 250)}.{random.randint(1, 254)}"


def _safe_port(s: str, default: int) -> int:
    try:
        p = int(str(s).strip())
        return max(0, min(65535, p))
    except (TypeError, ValueError):
        return default


def _proto_key(protocol: str) -> str:
    p = (protocol or "").upper()
    if "DNS" in p:
        return "DNS"
    if "ICMP" in p:
        return "ICMP"
    if "UDP" in p:
        return "UDP"
    return "TCP"


def _default_port_for_protocol(protocol: str, transport: str) -> int:
    p = (protocol or "").upper()
    if transport == "DNS":
        return 53
    if "FTP" in p:
        return 21
    if "HTTP" in p:
        return 80
    if "TLS" in p or "HTTPS" in p:
        return 443
    if "SMTP" in p:
        return 25
    if transport == "UDP":
        return 53
    return 80


def _inject_flag_into_payload(payload: str, flag_line: str) -> str:
    if flag_line in payload:
        return payload
    return payload.replace("{{FLAG}}", flag_line).replace("{FLAG}", flag_line)


def _clean_payload_without_flag(payload: str, flag_line: str) -> str:
    """Remove exact flag line from payload while preserving other text."""
    if not payload:
        return payload
    cleaned = payload.replace(flag_line, "").replace("{{FLAG}}", "").replace("{FLAG}", "")
    # Remove any FLAG = "..." / FLAG='...' variant the model may have repeated
    # with spacing/casing differences across packets.
    cleaned = re.sub(r"FLAG\s*=\s*['\"][^'\"]*['\"]", "", cleaned, flags=re.IGNORECASE)
    # Normalize excessive blank lines after removal
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")
    return cleaned.strip("\n")


def _expand_flag_placeholders(payload: str, flag_line: str) -> str:
    """Expand explicit placeholders only in the selected injection packet."""
    if not payload:
        return payload
    return payload.replace("{{FLAG}}", flag_line).replace("{FLAG}", flag_line)


def _clean_fragment_placeholder_payload(payload: str) -> str:
    """
    Remove LLM placeholder fragment text like:
    data=fragment_1;part=1|file.txt
    so the challenge relies on generated part=n; data=... fragments only.
    """
    if not payload:
        return payload
    text = payload
    text = re.sub(r"\bfragment\s+\d+\s+of\s+\d+\b", "", text, flags=re.IGNORECASE)
    # If model already stuffed multiple "part/data" segments in one line,
    # drop it so real one-fragment-per-packet injection remains authoritative.
    if "part=" in text.lower() and "data=" in text.lower():
        return ""
    text = re.sub(r"data=fragment_\d+;part=\d+\|file\.txt", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bfragment_\d+\b", "", text, flags=re.IGNORECASE)
    # Remove common verbose template lines that LLMs repeat across many packets.
    text = re.sub(
        r"\bthis is the (first|second|third|fourth|\d+(?:st|nd|rd|th))\s+fragment[^\n]*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\bfragment of a larger packet[^\n]*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_fragments(value: str, count: int) -> List[str]:
    value = value or ""
    count = max(2, min(16, count))
    # Avoid generating many empty duplicate chunks when requested count > data length.
    count = min(count, max(2, len(value))) if value else 2
    size = max(1, (len(value) + count - 1) // count)
    parts = [value[i : i + size] for i in range(0, len(value), size)]
    while len(parts) < count:
        parts.append("")
    return parts[:count]


def _fragment_flow_seed(packets_spec: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Pick realistic flow defaults for fragment packets from the plan itself
    instead of hard-coded demo endpoints.
    """
    if packets_spec:
        for spec in reversed(packets_spec):
            if not isinstance(spec, dict):
                continue
            src_ip = _safe_ip(str(spec.get("src_ip", "10.11.12.1")))
            dst_ip = _safe_ip(str(spec.get("dst_ip", "10.11.12.2")))
            raw_proto = str(spec.get("protocol", "TCP")).upper()
            proto = _proto_key(raw_proto)
            default_dport = _default_port_for_protocol(raw_proto, proto)
            sport = _safe_port(spec.get("src_port", "44444"), 44444)
            dport = _safe_port(spec.get("dst_port", str(default_dport)), default_dport)
            if dport == 0:
                dport = default_dport
            return {
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "raw_proto": raw_proto,
                "proto": proto,
                "sport": sport,
                "dport": dport,
            }
    return {
        "src_ip": "10.11.12.1",
        "dst_ip": "10.11.12.2",
        "raw_proto": "TCP",
        "proto": "TCP",
        "sport": 44444,
        "dport": 8080,
    }


def build_packets_from_plan(
    plan: Dict[str, Any],
    display_flag_line: str,
    answer_flag: str,
    fragmentation: bool = False,
    fragment_count: int = 1,
) -> List[Any]:
    """Return list of Scapy packets."""
    if wrpcap is None:
        raise RuntimeError("Scapy is required to build PCAP files.")

    display_inner = extract_flag_inner_value(display_flag_line) or (display_flag_line or "").strip()
    flag_line = canonical_flag_line(display_inner)
    answer_plain = (answer_flag or "").strip()
    fragmentation = parse_bool(fragmentation, False)
    fragment_count = coerce_fragment_count(fragment_count, 4 if fragmentation else 1)
    packets_spec: List[Dict[str, Any]] = plan.get("packets") or []
    pkts: List[Any] = []
    base_time = time.time() - random.randint(300, 86400)
    delta = 0.001
    tcp_state: Dict[Any, Dict[str, int]] = {}

    inject_index = len(packets_spec) - 1 if packets_spec else None

    flag_embedded = False
    seen_fragment_payloads = set()
    for idx, spec in enumerate(packets_spec):
        src_ip = _safe_ip(str(spec.get("src_ip", "10.0.0.1")))
        dst_ip = _safe_ip(str(spec.get("dst_ip", "10.0.0.2")))
        raw_proto = str(spec.get("protocol", "TCP")).upper()
        proto = _proto_key(raw_proto)
        raw_payload = spec.get("payload")
        payload = raw_payload if isinstance(raw_payload, str) else ""

        # Remove full flag artifacts from baseline payloads; we will inject safely below.
        payload = _clean_payload_without_flag(payload, flag_line)
        if display_inner:
            payload = payload.replace(display_inner, "")
        if answer_plain:
            payload = payload.replace(answer_plain, "")
        if fragmentation:
            payload = _clean_fragment_placeholder_payload(payload)
            if payload:
                norm = payload.strip().lower()
                if norm in seen_fragment_payloads:
                    payload = ""
                else:
                    seen_fragment_payloads.add(norm)
            # In fragmentation mode, keep capture deterministic and easy to solve:
            # authoritative evidence is emitted below as dedicated part=n packets.
            # We intentionally skip baseline plan packets to avoid mixed/duplicated views.
            continue

        if not fragmentation:
            if idx == inject_index:
                payload = _expand_flag_placeholders(payload, flag_line)
                if flag_line not in payload:
                    payload = payload + ("\n" if payload and not payload.endswith("\n") else "") + flag_line
            if flag_line in payload:
                flag_embedded = True

        default_dport = _default_port_for_protocol(raw_proto, proto)
        sport = _safe_port(spec.get("src_port", "49152"), 49152)
        dport = _safe_port(spec.get("dst_port", str(default_dport)), default_dport)
        if dport == 0:
            dport = default_dport
        # If model returns generic web ports for non-web protocols, coerce to protocol-typical ports.
        if "FTP" in raw_proto and dport in (80, 443, 8080):
            dport = 21
        elif "SMTP" in raw_proto and dport in (80, 443, 8080):
            dport = 25
        elif "DNS" in raw_proto:
            dport = 53

        ts = base_time + delta
        delta += random.uniform(0.002, 0.08)

        if proto == "ICMP":
            icmp_type = 8 if "echo" in payload.lower() or sport == 0 else 0
            pkt = IP(src=src_ip, dst=dst_ip) / ICMP(type=icmp_type) / Raw(load=payload.encode("utf-8", errors="replace"))
        elif proto == "DNS":
            if dport != 53:
                dport = 53
            extra = payload.encode("utf-8", errors="replace")
            if (not fragmentation) and idx == inject_index and flag_line.encode() not in extra:
                extra = (payload + "\n" + flag_line).encode("utf-8", errors="replace")
                flag_embedded = True
            pkt = IP(src=src_ip, dst=dst_ip) / UDP(sport=sport, dport=dport) / Raw(load=extra)
        elif proto == "UDP":
            pkt = IP(src=src_ip, dst=dst_ip) / UDP(sport=sport, dport=dport) / Raw(load=payload.encode("utf-8", errors="replace"))
        else:
            key = (src_ip, dst_ip, sport, dport)
            reverse_key = (dst_ip, src_ip, dport, sport)
            payload_bytes = payload.encode("utf-8", errors="replace")
            payload_len = max(1, len(payload_bytes))
            st = tcp_state.get(key)
            if st is None:
                st = {"next_seq": random.randint(1000, 900000)}
                tcp_state[key] = st
            seq = st["next_seq"]
            ack = 1
            rev = tcp_state.get(reverse_key)
            if rev is not None:
                ack = rev["next_seq"]
            st["next_seq"] += payload_len
            pkt = IP(src=src_ip, dst=dst_ip) / TCP(sport=sport, dport=dport, flags="PA", seq=seq, ack=ack) / Raw(load=payload_bytes)

        pkt.time = ts
        pkts.append(pkt)

    if fragmentation:
        fragment_target = display_inner
        fragments = _split_fragments(fragment_target, fragment_count)
        # Emit dedicated fragment packets with stable flow metadata and contiguous
        # transport state so Wireshark does not show artificial missing-segment noise.
        flow = _fragment_flow_seed(packets_spec)
        frag_src = flow["src_ip"]
        frag_dst = flow["dst_ip"]
        frag_proto = flow["proto"]
        frag_sport = int(flow["sport"])
        frag_dport = int(flow["dport"])
        transfer_id = secrets.token_hex(4)
        tcp_seq = random.randint(1000, 900000)
        for i, frag in enumerate(fragments):
            frag_payload = (
                f"part={i+1}; total={len(fragments)}; transfer={transfer_id}; "
                f"flag_part={i+1}; data={frag}\n"
            )
            frag_bytes = frag_payload.encode("utf-8", errors="replace")
            # Put each part on its own conversation so Follow TCP Stream
            # shows one fragment line at a time instead of a concatenated stream.
            per_part_sport = max(1, min(65535, frag_sport + i))
            if frag_proto == "ICMP":
                pkt = IP(src=frag_src, dst=frag_dst) / ICMP(type=8) / Raw(load=frag_bytes)
            elif frag_proto == "DNS":
                pkt = IP(src=frag_src, dst=frag_dst) / UDP(sport=per_part_sport, dport=53) / Raw(load=frag_bytes)
            elif frag_proto == "UDP":
                pkt = IP(src=frag_src, dst=frag_dst) / UDP(sport=per_part_sport, dport=frag_dport) / Raw(load=frag_bytes)
            else:
                pkt = (
                    IP(src=frag_src, dst=frag_dst)
                    / TCP(sport=per_part_sport, dport=frag_dport, flags="PA", seq=tcp_seq, ack=1)
                    / Raw(load=frag_bytes)
                )
                tcp_seq += max(1, len(frag_bytes))
            pkt.time = base_time + delta
            delta += random.uniform(0.002, 0.08)
            pkts.append(pkt)
        flag_embedded = True

    if not fragmentation and not flag_embedded:
        # Guarantee flag on wire
        a, b = "10.11.12.1", "10.11.12.2"
        pkts.append(
            IP(src=a, dst=b)
            / TCP(sport=44444, dport=80, flags="PA", seq=1, ack=1)
            / Raw(load=flag_line.encode("utf-8"))
        )
        pkts[-1].time = base_time + delta

    return pkts


def write_pcap_with_tshark(packets: List[Any], final_path: str) -> None:
    """Write packets via Scapy then round-trip through tshark for pcapng compatibility."""
    if wrpcap is None:
        raise RuntimeError("Scapy is required.")

    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    tshark = shutil.which("tshark")
    with tempfile.NamedTemporaryFile(suffix=".pcapng", delete=False) as tmp1:
        tmp1_path = tmp1.name
    try:
        wrpcap(tmp1_path, packets)
        if tshark:
            try:
                subprocess.run(
                    [tshark, "-r", tmp1_path, "-w", final_path, "-F", "pcapng"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                wrpcap(final_path, packets)
        else:
            wrpcap(final_path, packets)
    finally:
        try:
            os.unlink(tmp1_path)
        except OSError:
            pass


def make_ai_pcap_filename(user_id: int) -> str:
    """Safe unique filename under pcaps/."""
    suffix = secrets.token_hex(6)
    return f"ai_u{user_id}_{suffix}.pcapng"
