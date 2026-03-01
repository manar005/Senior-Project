"""
Challenges module - Loads all challenges from category folders.
Each protocol has its own folder; TCP has 3 challenges (handshake, count, fragmentation).
"""
from .http.challenge_01 import challenge as challenge_01
from .tcp.challenge_02 import challenge as challenge_02
from .tcp.challenge_07 import challenge as challenge_07
from .tcp.challenge_08 import challenge as challenge_08
from .dns.challenge_03 import challenge as challenge_03
from .ftp.challenge_04 import challenge as challenge_04
from .icmp.challenge_05 import challenge as challenge_05
from .smtp.challenge_06 import challenge as challenge_06
from .tls.challenge_09 import challenge as challenge_09
from .forensics.challenge_10 import challenge as challenge_10


def get_network_challenges():
    """Returns all network challenges in global order (for DB insert: id 1→ch01, 2→ch02, … 8→ch08, 9→ch09, 10→ch10 so pcap links work).
    Category grouping (TCP, etc.) is done via category_slug when inserting into DB.
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
    ]
