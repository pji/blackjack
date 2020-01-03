"""
players
~~~~~~~

The module contains the basic classes used by blackjack for handling 
players, including the dealer.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from blackjack.cards import Hand


# Global values.
HIT = True
STAND = False


# will_hit functions.
def dealer_will_hit(self, hand):
    """Determine whether the player will hit or stand on the hand.
    
    :param hand: The hand to make the decision on.
    :return: The hit decision. True to hit. False to stand.
    :rtype: Bool.
    """
    score = sorted(hand.score())[-1]
    if score >= 17:
        return STAND
    return HIT


class Player:
    """A blackjack player."""
    def __init__(self, hands: tuple = ()) -> None:
        """Initialize and instance of the class.
        
        :param hands: The player's hands of blackjack.
        :return: None.
        :rtype: None.
        """
        self.hands = hands