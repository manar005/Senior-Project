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

def get_network_challenges():
    """Returns a list of all network security challenges in order (1-10)"""
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
