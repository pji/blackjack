"""
willhit
~~~~~~~

The module contains the will_hit decision functions for players. These 
determine whether the player will hit or stand. They must:

* Accept self
* Accept a cards.Hand object
* Accept a game.Engine object
* Return a bool

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from random import choice

from blackjack.cards import Hand


# Global values.
HIT = True
STAND = False


# Functions.
def will_hit_dealer(self, hand:Hand, the_game=None) -> bool:
    """Determine whether the player will hit or stand on the hand.
    
    :param hand: The hand to make the decision on.
    :return: The hit decision. True to hit. False to stand.
    :rtype: Bool.
    """
    scores = [score for score in sorted(hand.score()) if score <= 21]
    try:
        score = scores[-1]
    except IndexError:
        return STAND
    else:
        if score >= 17:
            return STAND
        return HIT

def will_hit_never(self, hand:Hand, the_game=None) -> bool:
    """Never hit."""
    return False

def will_hit_random(self, hand:Hand, the_game: 'game.Engine' = None) -> bool:
    """Decide whether to hit at random."""
    return choice([True, False])

def will_hit_recommended(self, hand:Hand, the_game) -> bool:
    """Make hit decisions as recommended by bicycle.com."""
    dhand = the_game.dealer.hands[0]
    scores = [score for score in hand.score() if score <= 21]
    try:
        score = scores.pop()
    except IndexError:
        return False
    if scores and score <= 18:
        return True
    elif (dhand[0].rank >= 7 or dhand[0].rank == 1) and score < 17:
        return True
    elif dhand[0].rank <= 3 and score < 13:
        return True
    elif score < 12:
        return True
    return False

def will_hit_user(self, hand:Hand, the_game) -> bool:
    """Get a hit decision from the user."""
    is_yes = the_game.ui.hit_prompt()
    
    return is_yes.value


# List of valid will_hit functions.
# The following must be true to avoid unexpected behavior in randomly 
# generated players:
#   * The user version must be at index 0.
#   * The dealer version must be at index 1.
will_hits = [
    will_hit_user, 
    will_hit_dealer, 
    will_hit_never, 
    will_hit_random,
    will_hit_recommended
]
