"""OpenAI-compatible chat completions for AI challenges. Key from GROK_API_KEY only (never logged).

Supports:
- **xAI Grok** — set ``GROK_PROVIDER=xai`` (recommended if you use a Grok key from console.x.ai), or leave
  ``GROK_PROVIDER`` unset and use a key that does **not** start with ``gsk_`` (Groq-style keys auto-route to Groq).
- **Groq** — keys starting with ``gsk_`` use Groq unless you override with ``GROK_PROVIDER=xai`` and point URL to xAI.
- **Custom** — set ``GROK_API_URL`` to the full ``.../v1/chat/completions`` URL and ``GROK_MODEL`` if needed.
"""
import json
import os
import re
import secrets
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Tuple

from thaghrah.ai.challenge_payload import extract_json_object, validate_grok_challenge_payload

XAI_CHAT_URL = "https://api.x.ai/v1/chat/completions"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
# xAI model ids change; `grok-3-mini` is often unavailable on new keys. `grok-4` is the current default in xAI docs.
DEFAULT_XAI_MODEL = "grok-4"
# Fast, widely available on Groq Cloud; override with GROK_MODEL if you prefer 70B etc.
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"

# If .env points at xAI but GROK_MODEL is a Groq-style id (or the reverse), fix it so requests don’t 400.
_GROQ_LIKE_MODEL_PREFIXES = (
    "llama-",
    "mixtral-",
    "gemma",
    "meta-llama/",
    "openai/gpt-oss",
    "qwen/",
    "whisper-",
)


# Older examples use these; many accounts now get 400 on chat/completions — use current default instead.
_XAI_MODELS_UPGRADE_TO_DEFAULT = frozenset({"grok-3-mini", "grok-3"})


def _coerce_model_for_endpoint(chat_url: str, model_name: str) -> str:
    m = (model_name or "").strip()
    low = m.lower()
    if not m:
        return DEFAULT_XAI_MODEL if "x.ai" in chat_url.lower() else DEFAULT_GROQ_MODEL
    if "x.ai" in chat_url.lower():
        if low in _XAI_MODELS_UPGRADE_TO_DEFAULT:
            print(
                f"[Thaghrah AI] GROK_MODEL {m!r} is often unavailable on current xAI; using {DEFAULT_XAI_MODEL!r}.",
                file=sys.stderr,
            )
            return DEFAULT_XAI_MODEL
        if any(low.startswith(p) for p in _GROQ_LIKE_MODEL_PREFIXES) or "/" in m:
            print(
                f"[Thaghrah AI] GROK_MODEL {m!r} is not valid on xAI; using {DEFAULT_XAI_MODEL!r} instead.",
                file=sys.stderr,
            )
            return DEFAULT_XAI_MODEL
    if "groq.com" in chat_url.lower():
        if low.startswith("grok"):
            print(
                f"[Thaghrah AI] GROK_MODEL {m!r} is not valid on Groq; using {DEFAULT_GROQ_MODEL!r} instead.",
                file=sys.stderr,
            )
            return DEFAULT_GROQ_MODEL
    return m


def _chat_url_and_model(api_key: str) -> Tuple[str, str]:
    """Resolve endpoint and model from env; never read secrets beyond the key prefix."""
    url = (os.environ.get("GROK_API_URL") or "").strip()
    model = (os.environ.get("GROK_MODEL") or "").strip()
    provider = (os.environ.get("GROK_PROVIDER") or "auto").strip().lower()

    if url:
        if not model:
            if "groq.com" in url.lower():
                model = DEFAULT_GROQ_MODEL
            else:
                model = DEFAULT_XAI_MODEL
        return url, model

    # Force xAI Grok even if the key string looks like another provider’s format.
    if provider in ("xai", "grok", "x"):
        return XAI_CHAT_URL, model or DEFAULT_XAI_MODEL
    if provider in ("groq", "groqcloud", "groq_cloud"):
        return GROQ_CHAT_URL, model or DEFAULT_GROQ_MODEL

    # auto (or unknown provider value): infer from key prefix
    if api_key.startswith("gsk_"):
        return GROQ_CHAT_URL, model or DEFAULT_GROQ_MODEL
    return XAI_CHAT_URL, model or DEFAULT_XAI_MODEL


def _friendly_api_http_error(status: int, body_text: str, chat_url: str = "") -> str:
    """User-safe message; body_text must not contain secrets (API bodies usually do not)."""
    low = (body_text or "").lower()
    is_xai = "x.ai" in chat_url.lower()
    is_groq = "groq.com" in chat_url.lower()
    if status == 401:
        return "The API rejected your key (401). Check GROK_API_KEY in .env, save, and restart the server."
    if status == 403:
        return "The API refused this request (403). Check your Groq/xAI account access or model permissions."
    if status == 429:
        return "Rate limit reached (429). Wait a short time and try again."
    if status == 400:
        if "model" in low and any(x in low for x in ("not found", "does not exist", "invalid_model", "invalid model")):
            if is_xai:
                return (
                    "The model name is not valid for xAI Grok (400). In .env set GROK_MODEL to an id from "
                    "console.x.ai (e.g. grok-4 or grok-4-latest). Remove GROK_MODEL to use the app default. "
                    "Do not use Groq names (llama-…). Restart the server after editing .env."
                )
            if is_groq:
                return (
                    "The model name is not valid on Groq (400). In .env set GROK_MODEL to a current Groq model id "
                    "(e.g. llama-3.1-8b-instant), then restart the server."
                )
            return (
                "The model name is not valid for this provider (400). Set GROK_MODEL to a model id that matches "
                "your provider (xAI console for Grok, or Groq console for Groq), then restart the server."
            )
        if "max_tokens" in low or "max_completion" in low:
            return "The AI provider rejected request parameters (400). Restart the server after updating the app."
    return (
        "The AI service returned an error. Check the terminal where you run `python run.py` for a "
        "[Thaghrah AI] log line with details. You can also try a shorter prompt or set GROK_MODEL in .env."
    )


def _log_ai_http_error(status: int, url: str, body_text: str) -> None:
    host = urllib.parse.urlparse(url).netloc or url
    snippet = (body_text or "")[:600].replace("\n", " ")
    print(f"[Thaghrah AI] HTTP {status} from {host}: {snippet}", file=sys.stderr)


def _request_headers(api_key: str) -> Dict[str, str]:
    """Headers chosen to work with provider edge/CDN checks."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "ThaghrahAI/1.0 (+https://thaghrah.local)",
    }


def _post_with_urllib(chat_url: str, data: bytes, headers: Dict[str, str], timeout_sec: int, ctx) -> str:
    req = urllib.request.Request(chat_url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _extract_message_text(message: Dict[str, Any]) -> str:
    """Handle provider variants: content as string or content parts list."""
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                txt = part.get("text") or part.get("content") or ""
                if isinstance(txt, str):
                    parts.append(txt)
            elif isinstance(part, str):
                parts.append(part)
        return "\n".join([x for x in parts if x])
    return ""


def _repair_to_json_via_llm(chat_url: str, api_key: str, raw_text: str, timeout_sec: int) -> Optional[Dict[str, Any]]:
    """Second-pass repair: convert near-JSON response into strict JSON object."""
    if not raw_text.strip():
        return None
    headers = _request_headers(api_key)
    repair_prompt = (
        "Convert the following model output into exactly one valid JSON object matching the required schema. "
        "Return JSON only, no markdown, no comments. Keep fields faithful; do not invent missing nested packet data. "
        "If uncertain, use safe defaults while preserving intent.\n\nRAW_OUTPUT:\n" + raw_text[:12000]
    )
    body = {
        "model": _coerce_model_for_endpoint(chat_url, (os.environ.get("GROK_MODEL") or "").strip()),
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": "You are a strict JSON formatter."},
            {"role": "user", "content": repair_prompt},
        ],
    }
    cap = max(512, min(2048, _completion_token_limit()))
    if "groq.com" in chat_url.lower():
        body["max_completion_tokens"] = cap
    else:
        body["max_tokens"] = cap

    data = json.dumps(body).encode("utf-8")
    ctx = ssl.create_default_context()
    try:
        raw = _post_with_urllib(chat_url, data, headers, timeout_sec, ctx)
        api_json = json.loads(raw)
        choices = api_json.get("choices") or []
        if not choices:
            return None
        message = choices[0].get("message") or {}
        fixed_text = _extract_message_text(message)
        return extract_json_object(fixed_text)
    except Exception:
        return None

def _infer_protocol_from_text(text: str) -> str:
    low = (text or "").lower()
    mapping = [
        ("http", "HTTP"),
        ("dns", "DNS"),
        ("ftp", "FTP"),
        ("icmp", "ICMP"),
        ("smtp", "SMTP"),
        ("tls", "TLS"),
        ("tcp", "TCP"),
        ("forensic", "Forensics"),
        ("encryption", "TLS"),
    ]
    for key, proto in mapping:
        if key in low:
            return proto
    return "TCP"


def _requested_protocol_from_prompt(prompt: str) -> Optional[str]:
    low = (prompt or "").lower()
    ordered = [
        ("forensics", "Forensics"),
        ("http", "HTTP"),
        ("tcp", "TCP"),
        ("dns", "DNS"),
        ("ftp", "FTP"),
        ("icmp", "ICMP"),
        ("smtp", "SMTP"),
        ("tls", "TLS"),
    ]
    for key, proto in ordered:
        if key in low:
            return proto
    return None


def _extract_json_string_field(raw_text: str, key: str) -> Optional[str]:
    pat = re.compile(rf'"{re.escape(key)}"\s*:\s*"', re.IGNORECASE)
    m = pat.search(raw_text or "")
    if not m:
        return None
    i = m.end()
    out = []
    escaped = False
    while i < len(raw_text):
        ch = raw_text[i]
        if escaped:
            out.append(ch)
            escaped = False
        elif ch == "\\":
            escaped = True
        elif ch == '"':
            return "".join(out).strip() or None
        else:
            out.append(ch)
        i += 1
    return "".join(out).strip() or None


def _best_effort_payload_from_partial(raw_text: str, user_prompt: str) -> Dict[str, Any]:
    combined = (raw_text or "") + "\n" + (user_prompt or "")
    protocol = _infer_protocol_from_text(combined)
    title = _extract_json_string_field(raw_text, "title") or f"AI {protocol} challenge"
    description = _extract_json_string_field(raw_text, "description") or (
        f"Analyze this {protocol} capture, identify suspicious traffic behavior, and recover the embedded flag."
    )
    hint = _extract_json_string_field(raw_text, "hint") or (
        "1) Open the PCAP in Wireshark.\n"
        "2) Apply protocol-focused filters to isolate suspicious flows.\n"
        "3) Follow the relevant stream/conversation and inspect payloads.\n"
        "4) Reassemble encoded or fragmented content if needed.\n"
        "5) Locate a payload line in the format FLAG = \"...\".\n"
        "6) Submit only the value inside the quotes."
    )
    outcome = _extract_json_string_field(raw_text, "outcome") or (
        f"Build practical skill in investigating {protocol} traffic and extracting indicators from packet-level evidence."
    )
    difficulty = _extract_json_string_field(raw_text, "difficulty") or "medium"

    points = 100
    pm = re.search(r'"points"\s*:\s*(\d+)', raw_text or "")
    if pm:
        try:
            points = max(10, min(500, int(pm.group(1))))
        except ValueError:
            points = 100

    answer_flag = _extract_json_string_field(raw_text, "answer_flag") or f"THAG_AI_{secrets.token_hex(4).upper()}"
    display_flag = _extract_json_string_field(raw_text, "display_flag") or f'FLAG = "{answer_flag}"'

    dport = "443" if protocol in ("HTTP", "TLS") else "8080"
    packets = [
        {"protocol": protocol, "src_ip": "192.168.1.100", "dst_ip": "192.168.1.200", "src_port": "51515", "dst_port": dport, "payload": "Session start"},
        {"protocol": protocol, "src_ip": "192.168.1.200", "dst_ip": "192.168.1.100", "src_port": dport, "dst_port": "51515", "payload": "Server response"},
        {"protocol": protocol, "src_ip": "192.168.1.100", "dst_ip": "192.168.1.200", "src_port": "51515", "dst_port": dport, "payload": "Encoded marker: QXR0YWNrX2Zsb3c="},
        {"protocol": protocol, "src_ip": "192.168.1.200", "dst_ip": "192.168.1.100", "src_port": dport, "dst_port": "51515", "payload": display_flag},
    ]

    return {
        "title": title,
        "description": description,
        "hint": hint,
        "outcome": outcome,
        "points": points,
        "protocol": protocol,
        "difficulty": difficulty,
        "display_flag": display_flag,
        "answer_flag": answer_flag,
        "encoding": "none",
        "fragmentation": False,
        "fragment_count": 1,
        "flag": display_flag,
        "pcap_plan": {
            "scenario": f"{protocol} communication with suspicious encoded/fragmented content.",
            "packets": packets,
            "wireshark_filters": [protocol.lower() if protocol != "Forensics" else "frame"],
            "encoding_or_obfuscation": "Base64",
        },
    }


def _normalize_text_consistency(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Keep wording consistent with scoring: the quoted value in FLAG = "..." is the exact submission.
    Challenges can require decoding clues/traffic, but not transformation of quoted flag value itself.
    """
    out = dict(payload or {})
    replacements = {
        "decode the flag": "decode traffic clues to locate the flag line",
        "decode the packet to reveal the flag": "analyze packet data to locate the flag line",
        "decode the packet": "analyze the packet data",
        "decode to reveal the flag": "analyze to locate the flag line",
    }
    for field in ("description", "hint", "outcome"):
        value = out.get(field)
        if not isinstance(value, str):
            continue
        txt = value
        for old, new in replacements.items():
            txt = txt.replace(old, new).replace(old.title(), new.capitalize())
        out[field] = txt
    return out


def _force_protocol_from_prompt(payload: Dict[str, Any], user_prompt: str) -> Dict[str, Any]:
    """If prompt explicitly asks for one protocol, enforce it in metadata and packets."""
    requested = _requested_protocol_from_prompt(user_prompt)
    if not requested:
        return payload
    out = dict(payload or {})
    out["protocol"] = requested
    plan = out.get("pcap_plan")
    if isinstance(plan, dict):
        packets = plan.get("packets")
        if isinstance(packets, list):
            for pkt in packets:
                if isinstance(pkt, dict):
                    pkt["protocol"] = requested
    return out


def _post_with_curl(chat_url: str, data: bytes, headers: Dict[str, str], timeout_sec: int) -> str:
    """Fallback for Groq 1010 edge blocks seen with some Python urllib fingerprints."""
    cmd = [
        "curl",
        "-sS",
        "--http1.1",
        "-X",
        "POST",
        chat_url,
        "--max-time",
        str(int(timeout_sec)),
        "--connect-timeout",
        "15",
    ]
    for k, v in headers.items():
        cmd.extend(["-H", f"{k}: {v}"])
    cmd.extend(["--data-binary", "@-"])
    proc = subprocess.run(cmd, input=data, capture_output=True, timeout=timeout_sec + 5)
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace")[:500]
        raise urllib.error.URLError(f"curl fallback failed: {stderr}")
    return proc.stdout.decode("utf-8", errors="replace")


def _structured_fallback_payload(user_prompt: str) -> Dict[str, Any]:
    """Compact second-pass prompt to regenerate valid JSON when first answer is truncated."""
    return {
        "title": "...",
        "description": "...",
        "hint": "...",
        "outcome": "...",
        "points": 100,
        "protocol": "...",
        "difficulty": "...",
        "display_flag": "FLAG = \"...\"",
        "answer_flag": "...",
        "encoding": "none",
        "fragmentation": False,
        "fragment_count": 1,
        "pcap_plan": {
            "scenario": "...",
            "packets": [
                {
                    "protocol": "...",
                    "src_ip": "...",
                    "dst_ip": "...",
                    "src_port": "...",
                    "dst_port": "...",
                    "payload": "..."
                }
            ],
            "wireshark_filters": ["..."],
            "encoding_or_obfuscation": "..."
        }
    }


def _regenerate_structured_json(chat_url: str, api_key: str, model_name: str, user_prompt: str, timeout_sec: int) -> Optional[Dict[str, Any]]:
    """Regenerate a compact strict-JSON challenge object when first response is malformed/truncated."""
    headers = _request_headers(api_key)
    schema_example = json.dumps(_structured_fallback_payload(user_prompt), ensure_ascii=True)
    system = (
        "Return exactly one valid JSON object and nothing else. Keep fields concise. "
        "Hint must be step-by-step but short (5-8 steps). Packets array length 4-8. "
        "display_flag must be format: FLAG = \"VALUE\". answer_flag must be plain decoded answer."
    )
    user = (
        "Build a network packet analysis challenge from this prompt:\n"
        + user_prompt[:1200]
        + "\n\nUse this exact key structure and fill values:\n"
        + schema_example
    )
    body = {
        "model": model_name,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    cap = max(768, min(2048, _completion_token_limit()))
    if "groq.com" in chat_url.lower():
        body["max_completion_tokens"] = cap
        body["response_format"] = {"type": "json_object"}
    else:
        body["max_tokens"] = cap

    data = json.dumps(body).encode("utf-8")
    ctx = ssl.create_default_context()
    try:
        raw = _post_with_urllib(chat_url, data, headers, timeout_sec, ctx)
        api_json = json.loads(raw)
        choices = api_json.get("choices") or []
        if not choices:
            return None
        message = choices[0].get("message") or {}
        txt = _extract_message_text(message)
        return extract_json_object(txt)
    except Exception:
        return None


def _completion_token_limit() -> int:
    """Provider-safe completion token cap (overridable via GROK_MAX_COMPLETION_TOKENS)."""
    raw = (os.environ.get("GROK_MAX_COMPLETION_TOKENS") or "").strip()
    if raw:
        try:
            return max(128, min(8192, int(raw)))
        except ValueError:
            pass
    # Default cap when env is unset (same value previously used for Groq and xAI).
    return 2048


SYSTEM_INSTRUCTIONS = """You are the challenge engine for Thaghrah, a cybersecurity PCAP learning lab.
The user describes what kind of packet-analysis challenge they want. You must invent a UNIQUE, realistic scenario
and output a single JSON object only (no markdown outside the JSON).

Infer from the user's prompt (do not use fixed templates):
- protocol focus: HTTP, TCP, DNS, FTP, ICMP, SMTP, TLS, or Forensics
- attack or scenario type when relevant (e.g. brute force, exfiltration, beaconing)
- encoding or obfuscation when relevant (Base64, XOR, fragmentation, cleartext, etc.)
- difficulty: easy, medium, or hard (infer if not stated)

Rules:
1) "hint": concise and accurate numbered steps (usually 5 lines). Explain where to look, whether to reconstruct parts, whether to decode, and what to submit.
2) "outcome": educational only — what concept the learner masters. NOT a walkthrough and NOT the flag.
3) Use BOTH:
   - "display_flag": exactly in this form: FLAG = \"...\" (this is the on-wire artifact in PCAP; may be encoded/obfuscated).
   - "answer_flag": plain decoded final value users must submit.
   If encoding is "none", display_flag inner value should match answer_flag.
4) Include:
   - "encoding": one of base64, hex, rot13, xor, none, custom
   - "fragmentation": true/false
   - "fragment_count": integer (>=2 if fragmentation true, else 1)
   Fragmentation and encoding are independent.
   If fragmentation=true and encoding!=none, encode answer_flag first, then fragment encoded value.
   If fragmentation=true and encoding=none, fragment plain answer_flag.
4) "pcap_plan": Describe packets to synthesize. Include 4–20 packets. Each packet object must have:
   protocol, src_ip, dst_ip, src_port, dst_port, payload
   - protocol: one of HTTP, TCP, UDP, DNS, ICMP, SMTP, FTP, TLS (TLS means TCP carrying TLS-looking bytes as cleartext payload for learning PCAPs), Forensics
   - IPs: use private ranges 10.x.x.x or 192.168.x.x
   - ports: integers as strings except ICMP can use "0"
   - payload: cleartext application bytes as a string. Include realistic suspicious clues.
   - For non-fragmented challenges, at least one payload can include display_flag.
   - For fragmented challenges, use payload fragments with markers like part=1; data=... and do NOT include full flag in every packet.
5) Vary IPs, ports, timestamps context in scenario text; every challenge must feel unique.

Return ONLY valid JSON matching this structure (no trailing commentary):
{
  "title": "...",
  "description": "...",
  "hint": "...",
  "outcome": "...",
  "points": 100,
  "protocol": "...",
  "difficulty": "...",
  "display_flag": "FLAG = \"...\"",
  "answer_flag": "...",
  "encoding": "base64 | hex | rot13 | xor | none | custom",
  "fragmentation": true,
  "fragment_count": 4,
  "pcap_plan": {
    "scenario": "...",
    "packets": [
      {
        "protocol": "...",
        "src_ip": "...",
        "dst_ip": "...",
        "src_port": "...",
        "dst_port": "...",
        "payload": "..."
      }
    ],
    "wireshark_filters": ["..."],
    "encoding_or_obfuscation": "..."
  }
}
"""


def call_grok_for_challenge(user_prompt: str, timeout_sec: int = 120) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Send user prompt to the configured LLM; return (success, message_or_error, validated_payload).
    On failure, error message is safe for clients (no secrets).
    """
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        return False, "AI challenge generation is not configured on this server.", None

    chat_url, model_name = _chat_url_and_model(api_key)
    model_name = _coerce_model_for_endpoint(chat_url, model_name)

    prompt = (user_prompt or "").strip()
    if not prompt:
        return False, "Please enter a prompt describing the challenge you want.", None
    if len(prompt) > 4000:
        return False, "Prompt is too long. Please shorten to 4000 characters or fewer.", None

    body = {
        "model": model_name,
        "temperature": 0.85,
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": prompt},
        ],
    }
    token_cap = _completion_token_limit()
    # Groq’s OpenAI-compatible API prefers max_completion_tokens; xAI still accepts max_tokens.
    if "groq.com" in chat_url.lower():
        body["max_completion_tokens"] = token_cap
        body["response_format"] = {"type": "json_object"}
    else:
        body["max_tokens"] = token_cap
    data = json.dumps(body).encode("utf-8")
    headers = _request_headers(api_key)

    ctx = ssl.create_default_context()
    try:
        raw = _post_with_urllib(chat_url, data, headers, timeout_sec, ctx)
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass

        # Groq JSON mode sometimes returns 400 json_validate_failed but includes
        # partially generated JSON in error.failed_generation. Recover from it.
        if (
            e.code == 400
            and "groq.com" in chat_url.lower()
            and "json_validate_failed" in (err_body or "")
        ):
            try:
                err_json = json.loads(err_body)
                failed_generation = (
                    (err_json.get("error") or {}).get("failed_generation") or ""
                )
                # Common Groq JSON-mode failure: model hit token limit before
                # emitting valid JSON. Regenerate with compact strict schema.
                if "max completion tokens reached" in failed_generation.lower():
                    regenerated = _regenerate_structured_json(chat_url, api_key, model_name, prompt, timeout_sec)
                    if regenerated:
                        regenerated = _normalize_text_consistency(regenerated)
                        regenerated = _force_protocol_from_prompt(regenerated, prompt)
                        ok, err, normalized = validate_grok_challenge_payload(regenerated)
                        if ok:
                            return True, "", normalized
                parsed = extract_json_object(failed_generation)
                if not parsed:
                    parsed = _best_effort_payload_from_partial(failed_generation, prompt)
                parsed = _normalize_text_consistency(parsed)
                parsed = _force_protocol_from_prompt(parsed, prompt)
                ok, err, normalized = validate_grok_challenge_payload(parsed)
                if ok:
                    return True, "", normalized
                salvage = _best_effort_payload_from_partial(failed_generation, prompt)
                salvage = _normalize_text_consistency(salvage)
                salvage = _force_protocol_from_prompt(salvage, prompt)
                ok, err, normalized = validate_grok_challenge_payload(salvage)
                if ok:
                    return True, "", normalized
            except Exception:
                pass

        # Groq may block some non-browser signatures at the edge (Cloudflare 1010).
        # Retry once with curl + explicit HTTP/1.1 headers before failing.
        if (
            e.code == 403
            and "groq.com" in chat_url.lower()
            and "1010" in (err_body or "")
        ):
            try:
                raw = _post_with_curl(chat_url, data, headers, timeout_sec)
            except (subprocess.SubprocessError, urllib.error.URLError, TimeoutError, OSError):
                _log_ai_http_error(e.code, chat_url, err_body)
                return False, _friendly_api_http_error(e.code, err_body, chat_url), None
        else:
            _log_ai_http_error(e.code, chat_url, err_body)
            return False, _friendly_api_http_error(e.code, err_body, chat_url), None
    except (urllib.error.URLError, TimeoutError, OSError):
        return False, "Could not reach the AI service. Check your connection and try again.", None

    try:
        api_json = json.loads(raw)
    except json.JSONDecodeError:
        return False, "Received an invalid response from the AI service.", None

    choices = api_json.get("choices")
    if not choices or not isinstance(choices, list):
        return False, "The AI response was incomplete. Please try again.", None

    message = choices[0].get("message") or {}
    content = _extract_message_text(message)
    if not content.strip():
        return False, "The AI response was incomplete. Please try again.", None

    parsed = extract_json_object(content)
    if not parsed:
        repaired = _repair_to_json_via_llm(chat_url, api_key, content, timeout_sec)
        if repaired:
            parsed = repaired

    if not parsed:
        regenerated = _regenerate_structured_json(chat_url, api_key, model_name, prompt, timeout_sec)
        if regenerated:
            parsed = regenerated
        else:
            parsed = _best_effort_payload_from_partial(content, prompt)

    parsed = _normalize_text_consistency(parsed)
    parsed = _force_protocol_from_prompt(parsed, prompt)
    ok, err, normalized = validate_grok_challenge_payload(parsed)
    if not ok:
        regenerated = _regenerate_structured_json(chat_url, api_key, model_name, prompt, timeout_sec)
        if regenerated:
            regenerated = _normalize_text_consistency(regenerated)
            regenerated = _force_protocol_from_prompt(regenerated, prompt)
            ok, err, normalized = validate_grok_challenge_payload(regenerated)
        if not ok:
            salvage = _best_effort_payload_from_partial(content, prompt)
            salvage = _normalize_text_consistency(salvage)
            salvage = _force_protocol_from_prompt(salvage, prompt)
            ok, err, normalized = validate_grok_challenge_payload(salvage)
        if not ok:
            _log_ai_http_error(422, chat_url, f"Validation failed after fallbacks: {err}")
            return False, "Generated challenge data failed validation. Please try again.", None

    return True, "", normalized
