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
    def __init__(self, hands: tuple = (), name: str = 'Player', 
                 chips: int = 0) -> None:
        """Initialize and instance of the class.
        
        :param hands: The player's hands of blackjack.
        :param name: The player's name.
        :param chips: The chips the player has for betting.
        :return: None.
        :rtype: None.
        """
        self.hands = hands
        self.name = name
        self.chips = chips
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        cls = self.__class__
        return f'{cls.__name__}[{self.name!r}]'
    
    def __format__(self, format_spec):
        return self.name.__format__(format_spec)


# will_hit functions.
# will_hit functions determine whether the player will hit or stand. 
# They must accept the following parameters:
#   * self
#   * A cards.Hand object
#   * A game.Game object
# 
# And they must return a bool.
def dealer_will_hit(self, hand:Hand, the_game=None) -> bool:
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
# will_split functions determine whether the player will split a hand. 
# They must accept the following parameters:
#   * self
#   * A cards.Hand object
#   * A game.Game object
# 
# And they must return a bool.
def always_will_split(self, hand:Hand, the_game=None) -> bool:
    """The player will always split where possible.
    
    :param hand: The hand that may be split.
    :return: The decision whether to split.
    :rtype: bool
    """
    return True
    

# will_buyin functions.
# will_buyin functions determine whether the player will buy into the 
# next round. They must accept the following parameters:
#   * self
#   * A cards.Hand object
#   * A game.Game object
# 
# And they must return a bool.
def always_will_buyin(self, the_game) -> bool:
    """The player will always try to buy into a game.
    
    :param game: The game to buy into.
    :return: Whether to buy into the game.
    :rtype: bool
    """
    return True


# will_double_down functions.
# will_double_down functions determine whether the player will double 
# down on a hand. They must accept the following parameters:
#   * self
#   * A cards.Hand object
#   * A game.Game object
# 
# And they must return a bool.
def will_double_down_always(self, hand:Hand, the_game) -> bool:
    """The player will always double down.
    
    :param hand: The hand to make the decision on.
    :param the_game: The information about the current game to use 
        to make a decision.
    :return: A decision whether to double down.
    :rtype: bool
    """
    return True


# will_insure functions.
# will_insure functions determine whether the player will buy 
# insurance for a hand. They must accept the following parameters:
#   * self
#   * A cards.Hand object
#   * A game.Game object
# 
# And they must return a bool or a float.
def will_insure_always(self, hand:Hand, the_game) -> bool:
    """The player will always buy insurance.
    
    :param hand: The hand to make the decision on.
    :param the_game: The information about the current game to use 
        to make a decision.
    :return: A decision whether to double down.
    :rtype: bool
    """
    return True


def playerfactory(name, will_hit_fn, will_split_fn, will_buyin_fn, 
                  will_double_down) -> type:
    """A factory function for Player subclasses."""
    attrs = {
        'will_hit': will_hit_fn,
        'will_split': will_split_fn,
        'will_buyin': will_buyin_fn,
        'will_double_down': will_double_down,
    }
    return type(name, (Player,), attrs)


# Player subclasses.
Dealer = playerfactory('Dealer', dealer_will_hit, None, None, None)
AutoPlayer = playerfactory('AutoPlayer', dealer_will_hit, always_will_split,
                            always_will_buyin, will_double_down_always)