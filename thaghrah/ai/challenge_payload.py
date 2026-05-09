"""Shared helpers for AI-generated challenges: flag parsing and Grok JSON validation."""
import json
import re
from typing import Any, Dict, List, Optional, Tuple


FLAG_LINE_PATTERN = re.compile(r'FLAG\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
VALID_ENCODINGS = {"base64", "hex", "rot13", "xor", "none", "custom"}


def extract_flag_inner_value(flag_field: str) -> Optional[str]:
    """Return the flag value inside quotes from FLAG = \"...\" or FLAG = '...'."""
    if not flag_field or not isinstance(flag_field, str):
        return None
    s = flag_field.strip()
    m = FLAG_LINE_PATTERN.search(s)
    if m:
        return m.group(1)
    # Plain value (no wrapper)
    s2 = s.strip()
    if s2 and not s2.upper().startswith("FLAG"):
        return s2
    return None


def canonical_flag_line(inner: str) -> str:
    """Exact on-wire format required for PCAP embedding."""
    inner = (inner or "").replace('"', "").replace("\r", "").replace("\n", "")
    return f'FLAG = "{inner}"'


def parse_bool(x: Any, default: bool = False) -> bool:
    if isinstance(x, bool):
        return x
    if isinstance(x, str):
        low = x.strip().lower()
        if low in ("1", "true", "yes", "y"):
            return True
        if low in ("0", "false", "no", "n"):
            return False
    if isinstance(x, (int, float)):
        return bool(x)
    return default


def coerce_fragment_count(x: Any, default: int = 4) -> int:
    try:
        n = int(x)
    except (TypeError, ValueError):
        n = default
    return max(2, min(16, n))


def trim_only(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _flag_words_from_text(value: Any) -> List[str]:
    s = trim_only(value).upper()
    # Split camel-case boundaries before normal symbol cleanup.
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"[^A-Z0-9]+", "_", s)
    words = [w for w in s.split("_") if w]
    return words


def normalize_ai_flag_value(
    value: Any,
    fallback_text: Any = "",
    protocol_hint: Any = "",
    target_words: int = 3,
    max_word_len: int = 12,
) -> str:
    """
    Normalize AI final flags to fixed-challenge style:
    UPPERCASE words joined by underscores, exactly 3 short meaningful words.
    """
    stop = {
        "THE", "AND", "FOR", "WITH", "FROM", "THIS", "THAT", "THEN", "INTO", "ONTO",
        "FLAG", "VALUE", "CHALLENGE", "NETWORK", "PACKET", "CAPTURE", "TRAFFIC",
    }
    words = _flag_words_from_text(value)
    # If the model gave one mashed token (e.g. SECRETPHISHF), enrich with title/protocol words.
    if len(words) < target_words:
        extra = [w for w in _flag_words_from_text(fallback_text) if w not in stop]
        if extra:
            words = extra
    if len(words) < target_words:
        p = _flag_words_from_text(protocol_hint) or ["AI"]
        words = words + p + ["FLAG", "CODE"]
    if len(words) < target_words:
        words = ["AI", "CHALLENGE", "FLAG"]
    words = [w[:max_word_len] for w in words[:target_words]]
    while len(words) < target_words:
        words.append("FLAG")
    return "_".join(words)


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Parse first JSON object from model output (handles ```json fences)."""
    if not text:
        return None
    t = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", t, re.IGNORECASE)
    if fence:
        t = fence.group(1).strip()
    start = t.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(t)):
        if t[i] == "{":
            depth += 1
        elif t[i] == "}":
            depth -= 1
            if depth == 0:
                chunk = t[start : i + 1]
                try:
                    return json.loads(chunk)
                except json.JSONDecodeError:
                    return None
    return None


def _is_non_empty_str(x: Any) -> bool:
    return isinstance(x, str) and len(x.strip()) > 0


def _coerce_points(x: Any) -> int:
    try:
        p = int(x)
    except (TypeError, ValueError):
        return 100
    return max(10, min(500, p))


def validate_grok_challenge_payload(data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validate Grok response shape. Returns (ok, error_message, normalized_dict).
    normalized_dict uses canonical keys and defaults for pcap_plan.
    """
    if not isinstance(data, dict):
        return False, "Invalid response structure", None

    required_top = ("title", "description", "hint", "outcome", "points", "protocol", "difficulty", "pcap_plan")
    for k in required_top:
        if k not in data:
            return False, f"Missing field: {k}", None

    if not all(_is_non_empty_str(data[k]) for k in ("title", "description", "hint", "outcome", "protocol", "difficulty")):
        return False, "Empty required text field", None

    display_flag_raw = data.get("display_flag")
    answer_flag_raw = data.get("answer_flag")

    # Backward-compatible salvage for old providers still sending `flag`.
    if not _is_non_empty_str(display_flag_raw) and _is_non_empty_str(data.get("flag")):
        display_flag_raw = data.get("flag")
    if not _is_non_empty_str(answer_flag_raw) and _is_non_empty_str(data.get("flag")):
        answer_flag_raw = extract_flag_inner_value(str(data.get("flag")))

    answer_flag = normalize_ai_flag_value(
        answer_flag_raw,
        fallback_text=data.get("title") or data.get("description"),
        protocol_hint=data.get("protocol"),
    )
    if not answer_flag:
        return False, "answer_flag is required and must not be empty", None

    display_raw = trim_only(display_flag_raw)
    display_inner = extract_flag_inner_value(display_raw)
    # Be tolerant to model drift: allow plain display value and canonicalize it.
    if not display_inner and display_raw:
        display_inner = display_raw
    if not display_inner:
        return False, 'display_flag must match FLAG = "..." with non-empty content', None
    display_flag = canonical_flag_line(display_inner)

    plan = data["pcap_plan"]
    if not isinstance(plan, dict):
        return False, "pcap_plan must be an object", None

    packets = plan.get("packets")
    if not isinstance(packets, list) or len(packets) == 0:
        return False, "pcap_plan.packets must be a non-empty array", None

    norm_packets: List[Dict[str, Any]] = []
    for i, pkt in enumerate(packets):
        if not isinstance(pkt, dict):
            return False, f"packets[{i}] must be an object", None
        for fld in ("protocol", "src_ip", "dst_ip"):
            if not _is_non_empty_str(pkt.get(fld)):
                return False, f"packets[{i}] missing {fld}", None
        norm_packets.append(
            {
                "protocol": str(pkt["protocol"]).strip(),
                "src_ip": str(pkt["src_ip"]).strip(),
                "dst_ip": str(pkt["dst_ip"]).strip(),
                "src_port": str(pkt.get("src_port") or "0").strip(),
                "dst_port": str(pkt.get("dst_port") or "0").strip(),
                "payload": pkt.get("payload") if isinstance(pkt.get("payload"), str) else "",
            }
        )

    wf = plan.get("wireshark_filters")
    if not isinstance(wf, list):
        wf = []
    wf = [str(x) for x in wf if isinstance(x, str) and x.strip()]

    enc = plan.get("encoding_or_obfuscation")
    if not isinstance(enc, str):
        enc = "none"
    encoding = str(data.get("encoding") or enc).strip().lower() or "none"
    if encoding not in VALID_ENCODINGS:
        encoding = "custom"
    # Keep non-encoded challenges in fixed-flag style.
    if encoding == "none":
        display_inner = normalize_ai_flag_value(
            display_inner,
            fallback_text=data.get("title") or data.get("description"),
            protocol_hint=data.get("protocol"),
        )
        display_flag = canonical_flag_line(display_inner)

    fragmentation = parse_bool(data.get("fragmentation"), False)
    fragment_count = coerce_fragment_count(data.get("fragment_count"), 4 if fragmentation else 1)
    if not fragmentation:
        fragment_count = 1

    if encoding != "none" and display_inner == answer_flag:
        return False, "display_flag cannot equal answer_flag when encoding is enabled", None

    scenario = plan.get("scenario")
    if not isinstance(scenario, str):
        scenario = ""

    normalized = {
        "title": str(data["title"]).strip()[:500],
        "description": str(data["description"]).strip()[:8000],
        "hint": str(data["hint"]).strip()[:16000],
        "outcome": str(data["outcome"]).strip()[:4000],
        "points": _coerce_points(data["points"]),
        "protocol": str(data["protocol"]).strip()[:120],
        "difficulty": str(data["difficulty"]).strip()[:120],
        "display_flag": display_flag,
        "answer_flag": answer_flag[:2000],
        "encoding": encoding,
        "fragmentation": fragmentation,
        "fragment_count": fragment_count,
        # Keep legacy `flag` key for compatibility with old call sites.
        "flag": display_flag,
        "pcap_plan": {
            "scenario": scenario.strip()[:4000],
            "packets": norm_packets,
            "wireshark_filters": wf[:20],
            "encoding_or_obfuscation": enc.strip()[:500],
        },
    }
    return True, "", normalized
