"""
Challenges module - Loads all challenges from individual files
"""
from .challenge_01 import challenge as challenge_01
from .challenge_02 import challenge as challenge_02
from .challenge_03 import challenge as challenge_03
from .challenge_04 import challenge as challenge_04
from .challenge_05 import challenge as challenge_05
from .challenge_06 import challenge as challenge_06
from .challenge_07 import challenge as challenge_07
from .challenge_08 import challenge as challenge_08
from .challenge_09 import challenge as challenge_09
from .challenge_10 import challenge as challenge_10
from .challenge_11 import challenge as challenge_11
from .challenge_12 import challenge as challenge_12
from .challenge_13 import challenge as challenge_13
from .challenge_14 import challenge as challenge_14
from .challenge_15 import challenge as challenge_15
from .challenge_16 import challenge as challenge_16
from .challenge_17 import challenge as challenge_17
from .challenge_18 import challenge as challenge_18
from .challenge_19 import challenge as challenge_19
from .challenge_20 import challenge as challenge_20

def get_all_challenges():
    """Returns a list of all challenges in order"""
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
    ]

def get_general_challenges():
    """Returns general cybersecurity challenges (1-10)"""
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

def get_network_challenges():
    """Returns network security challenges (11-20)"""
    return [
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
    ]
