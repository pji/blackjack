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


# Base class.
class Player:
    """A blackjack player."""
    def __init__(self, hands: tuple = (), name: str = 'Player') -> None:
        """Initialize and instance of the class.
        
        :param hands: The player's hands of blackjack.
        :return: None.
        :rtype: None.
        """
        self.hands = hands
        self.name = name
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        cls = self.__class__
        return f'{cls.__name__}[{self.name!r}]'
    
    def __format__(self, format_spec):
        return self.name.__format__(format_spec)


# will_hit functions.
def dealer_will_hit(self, hand):
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


# will_split functions.
def always_will_split(self, hand:Hand, *args, **kwargs) -> bool:
    """The player will always split where possible.
    
    :param hand: The hand that may be split.
    :return: The decision whether to split.
    :rtype: bool
    """
    return True
    

def playerfactory(name, will_hit_func, will_split_func) -> type:
    """A factory function for Player subclasses."""
    attrs = {
        'will_hit': will_hit_func,
        'will_split': will_split_func,
    }
    return type(name, (Player,), attrs)


# Player subclasses.
Dealer = playerfactory('Dealer', dealer_will_hit, None)
AutoPlayer = playerfactory('AutoPlayer', dealer_will_hit, always_will_split)