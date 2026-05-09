"""
AI Lab stack: Grok-compatible API client, challenge JSON validation / flags, PCAP assembly.
"""

from thaghrah.ai.challenge_payload import (
    extract_flag_inner_value,
    extract_json_object,
    normalize_ai_flag_value,
    parse_bool,
    trim_only,
    validate_grok_challenge_payload,
)
from thaghrah.ai.grok_client import call_grok_for_challenge
from thaghrah.ai.pcap_plan import build_packets_from_plan, make_ai_pcap_filename, write_pcap_with_tshark

__all__ = [
    "build_packets_from_plan",
    "call_grok_for_challenge",
    "extract_flag_inner_value",
    "extract_json_object",
    "make_ai_pcap_filename",
    "normalize_ai_flag_value",
    "parse_bool",
    "trim_only",
    "validate_grok_challenge_payload",
    "write_pcap_with_tshark",
]
