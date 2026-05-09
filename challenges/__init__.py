"""
Challenges module - Loads all challenges from category folders.
Each protocol has its own folder; TCP has 5 challenges.
"""
from .http.challenge_01 import challenge as challenge_01
from .tcp.challenge_06 import challenge as challenge_02
from .dns.challenge_11 import challenge as challenge_03
from .ftp.challenge_16 import challenge as challenge_04
from .icmp.challenge_21 import challenge as challenge_05
from .smtp.challenge_26 import challenge as challenge_06
from .tcp.challenge_07 import challenge as challenge_07
from .tcp.challenge_08 import challenge as challenge_08
from .tcp.challenge_09 import challenge as challenge_09
from .forensics.challenge_36 import challenge as challenge_10
from .forensics.challenge_37 import challenge as challenge_11
from .http.challenge_02 import challenge as challenge_12
from .http.challenge_03 import challenge as challenge_13
from .http.challenge_04 import challenge as challenge_14
from .http.challenge_05 import challenge as challenge_15
from .tls.challenge_31 import challenge as challenge_16
from .tcp.challenge_10 import challenge as challenge_17
from .dns.challenge_12 import challenge as challenge_18
from .dns.challenge_13 import challenge as challenge_19
from .dns.challenge_14 import challenge as challenge_20
from .dns.challenge_15 import challenge as challenge_21
from .ftp.challenge_17 import challenge as challenge_22
from .ftp.challenge_18 import challenge as challenge_23
from .ftp.challenge_19 import challenge as challenge_24
from .ftp.challenge_20 import challenge as challenge_25
from .icmp.challenge_22 import challenge as challenge_26
from .icmp.challenge_23 import challenge as challenge_27
from .icmp.challenge_24 import challenge as challenge_28
from .icmp.challenge_25 import challenge as challenge_29
from .smtp.challenge_27 import challenge as challenge_30
from .smtp.challenge_28 import challenge as challenge_31
from .smtp.challenge_29 import challenge as challenge_32
from .smtp.challenge_30 import challenge as challenge_33
from .tls.challenge_32 import challenge as challenge_34
from .tls.challenge_33 import challenge as challenge_35
from .tls.challenge_34 import challenge as challenge_36
from .tls.challenge_35 import challenge as challenge_37
from .forensics.challenge_38 import challenge as challenge_38
from .forensics.challenge_39 import challenge as challenge_39
from .forensics.challenge_40 import challenge as challenge_40


# Static PCAP filenames use ``challenge_%02d`` where ``%02d`` is a permutation of 1..40.
# CHALLENGE_PCAP_SUFFIXES[db_id - 1] is that suffix for ``challenges.id == db_id``.
CHALLENGE_PCAP_SUFFIXES = (
    1, 6, 11, 16, 21, 26, 7, 8, 9, 36,
    37, 2, 3, 4, 5, 31, 10, 12, 13, 14,
    15, 17, 18, 19, 20, 22, 23, 24, 25, 27,
    28, 29, 30, 32, 33, 34, 35, 38, 39, 40,
)

# For ``challenge_01`` … ``challenge_40`` (list order of ``get_network_challenges()``),
# static assets use ``challenge_{suffix}.pcapng`` with this suffix (matches source filenames).
STATIC_SUFFIX_BY_VARIABLE_INDEX = (
    1, 6, 11, 16, 21, 26, 7, 8, 9, 36, 37, 2, 3, 4, 5, 31, 10, 12, 13, 14,
    15, 17, 18, 19, 20, 22, 23, 24, 25, 27, 28, 29, 30, 32, 33, 34, 35, 38, 39, 40,
)

_DISPLAY_TO_CHALLENGE_ID = {
    display: idx for idx, display in enumerate(CHALLENGE_PCAP_SUFFIXES, start=1)
}


def pcap_suffix_for_challenge_id(challenge_id: int) -> int:
    """Map DB challenge primary key (1..40) to renamed challenge_%02d static files."""
    if not isinstance(challenge_id, int) or challenge_id < 1 or challenge_id > len(CHALLENGE_PCAP_SUFFIXES):
        return challenge_id if isinstance(challenge_id, int) else 1
    return CHALLENGE_PCAP_SUFFIXES[challenge_id - 1]


def display_number_for_challenge_id(challenge_id: int) -> int:
    """Public challenge number shown in URL/UI for a DB challenge id."""
    return pcap_suffix_for_challenge_id(challenge_id)


def challenge_id_for_display_number(display_number: int):
    """DB challenge id for a public/display challenge number, or None."""
    if not isinstance(display_number, int):
        return None
    return _DISPLAY_TO_CHALLENGE_ID.get(display_number)


def variable_index_for_static_suffix(suffix: int) -> int:
    """1-based index into ``get_network_challenges()`` for static ``challenge_{suffix}`` assets."""
    if suffix not in STATIC_SUFFIX_BY_VARIABLE_INDEX:
        raise ValueError(f"unknown static suffix: {suffix}")
    return STATIC_SUFFIX_BY_VARIABLE_INDEX.index(suffix) + 1


def challenge_dict_for_db_id(db_id: int):
    """Challenge metadata dict for ``challenges.id`` (matches PCAP/key naming via CHALLENGE_PCAP_SUFFIXES)."""
    if not isinstance(db_id, int) or db_id < 1 or db_id > len(CHALLENGE_PCAP_SUFFIXES):
        raise ValueError(f"db_id must be 1..{len(CHALLENGE_PCAP_SUFFIXES)}")
    suffix = CHALLENGE_PCAP_SUFFIXES[db_id - 1]
    vi = variable_index_for_static_suffix(suffix)
    return get_network_challenges()[vi - 1]


def get_network_challenges():
    """Returns all network challenges in global order (DB ids 1..40 = challenge_01..challenge_40).

    List order matches challenge module numbering so challenges.id aligns with challenge_NN.
    Unlock order in the UI still follows SQL (category id, then order_in_category), not this list order.

    Each dict uses:
    - order_in_category: sort position within that protocol on the UI (same name in DB).
    PCAP / key filenames: challenge_%02d with d = id (see CHALLENGE_PCAP_SUFFIXES).
    Category grouping uses category_id (challenge_categories.id) when inserting into DB.
    """
    return [
        challenge_01,
        challenge_02,
        challenge_03,
        challenge_04,
        challenge_05,
        challenge_06,
        challenge_07,
        challenge_08,
        challenge_09,
        challenge_10,
        challenge_11,
        challenge_12,
        challenge_13,
        challenge_14,
        challenge_15,
        challenge_16,
        challenge_17,
        challenge_18,
        challenge_19,
        challenge_20,
        challenge_21,
        challenge_22,
        challenge_23,
        challenge_24,
        challenge_25,
        challenge_26,
        challenge_27,
        challenge_28,
        challenge_29,
        challenge_30,
        challenge_31,
        challenge_32,
        challenge_33,
        challenge_34,
        challenge_35,
        challenge_36,
        challenge_37,
        challenge_38,
        challenge_39,
        challenge_40,
    ]
