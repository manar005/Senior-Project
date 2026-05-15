"""
Challenges module - Loads all challenges from category folders.

Global track order matches source file numbers:
  id N == challenges/*/challenge_NN.py == challenge_NN.pcapng == /challenge/N

HTTP 01-05, TCP 06-10, DNS 11-15, FTP 16-20, ICMP 21-25, SMTP 26-30, TLS 31-35, Forensics 36-40.
"""
from .http.challenge_01 import challenge as challenge_01
from .http.challenge_02 import challenge as challenge_02
from .http.challenge_03 import challenge as challenge_03
from .http.challenge_04 import challenge as challenge_04
from .http.challenge_05 import challenge as challenge_05
from .tcp.challenge_06 import challenge as challenge_06
from .tcp.challenge_07 import challenge as challenge_07
from .tcp.challenge_08 import challenge as challenge_08
from .tcp.challenge_09 import challenge as challenge_09
from .tcp.challenge_10 import challenge as challenge_10
from .dns.challenge_11 import challenge as challenge_11
from .dns.challenge_12 import challenge as challenge_12
from .dns.challenge_13 import challenge as challenge_13
from .dns.challenge_14 import challenge as challenge_14
from .dns.challenge_15 import challenge as challenge_15
from .ftp.challenge_16 import challenge as challenge_16
from .ftp.challenge_17 import challenge as challenge_17
from .ftp.challenge_18 import challenge as challenge_18
from .ftp.challenge_19 import challenge as challenge_19
from .ftp.challenge_20 import challenge as challenge_20
from .icmp.challenge_21 import challenge as challenge_21
from .icmp.challenge_22 import challenge as challenge_22
from .icmp.challenge_23 import challenge as challenge_23
from .icmp.challenge_24 import challenge as challenge_24
from .icmp.challenge_25 import challenge as challenge_25
from .smtp.challenge_26 import challenge as challenge_26
from .smtp.challenge_27 import challenge as challenge_27
from .smtp.challenge_28 import challenge as challenge_28
from .smtp.challenge_29 import challenge as challenge_29
from .smtp.challenge_30 import challenge as challenge_30
from .tls.challenge_31 import challenge as challenge_31
from .tls.challenge_32 import challenge as challenge_32
from .tls.challenge_33 import challenge as challenge_33
from .tls.challenge_34 import challenge as challenge_34
from .tls.challenge_35 import challenge as challenge_35
from .forensics.challenge_36 import challenge as challenge_36
from .forensics.challenge_37 import challenge as challenge_37
from .forensics.challenge_38 import challenge as challenge_38
from .forensics.challenge_39 import challenge as challenge_39
from .forensics.challenge_40 import challenge as challenge_40

_NETWORK_CHALLENGES = (
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
)


NETWORK_CHALLENGE_COUNT = len(_NETWORK_CHALLENGES)


def get_network_challenges():
    """All network challenges in global track order (index 0 == DB id 1)."""
    return list(_NETWORK_CHALLENGES)


def is_valid_network_challenge_id(challenge_id) -> bool:
    """True if challenge_id is a valid network track id (1..40)."""
    return isinstance(challenge_id, int) and 1 <= challenge_id <= NETWORK_CHALLENGE_COUNT


def challenge_dict_for_db_id(db_id: int):
    """Challenge metadata dict for ``challenges.id`` (1-based, matches challenge_NN.py)."""
    if not isinstance(db_id, int) or db_id < 1 or db_id > len(_NETWORK_CHALLENGES):
        raise ValueError(f"db_id must be 1..{len(_NETWORK_CHALLENGES)}")
    return _NETWORK_CHALLENGES[db_id - 1]
