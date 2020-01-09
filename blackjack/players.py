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
        self.insured = 0
    
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
    is_yes = the_game.ui.input('hit')
    return is_yes.value


# will_split functions.
# will_split functions determine whether the player will split a hand. 
# They must accept the following parameters:
#   * self
#   * A cards.Hand object
#   * A game.Game object
# 
# And they must return a bool.
def will_split_always(self, hand:Hand, the_game) -> bool:
    """The player will always split where possible.
    
    :param hand: The hand that may be split.
    :return: The decision whether to split.
    :rtype: bool
    """
    return True

def will_split_recommended(self, hand:Hand, the_game) -> bool:
    """Make a split decision as recommended by bicycle.com."""
    dhand = the_game.dealer.hands[0]
    if hand[0].rank == 1 or hand[0].rank == 8:
        return True
    elif hand[0].rank == 4 or hand[0].rank == 5 or hand[0].rank >= 10:
        return False
    elif hand[0].rank == 2 or hand[0].rank == 3 or hand[0].rank >= 7:
        if dhand[0].rank < 8 or dhand[0].rank == 1:
            return True
        else:
            return False
    else:
        if dhand[0].rank > 1 and dhand[0].rank < 7:
            return True
        else:
            return False

def will_split_user(self, hand:Hand, the_game) -> bool:
    """Get a split decision from the user."""
    is_yes = the_game.ui.input('split')
    return is_yes.value


# will_buyin functions.
# will_buyin functions determine whether the player will buy into the 
# next round. They must accept the following parameters:
#   * self
#   * A cards.Hand object
#   * A game.Game object
# 
# And they must return a bool.
def will_buyin_always(self, the_game) -> bool:
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

def will_double_down_recommended(self, hand:Hand, the_game) -> bool:
    """The player will follow the double down recommendation from 
    bicycle.com.
    :param hand: The hand to make the decision on.
    :param the_game: The information about the current game to use 
        to make a decision.
    :return: A decision whether to double down.
    :rtype: bool
    """
    scores = [score for score in hand.score() if score <= 21]
    dcard = the_game.dealer.hands[0][0]
    if 11 in scores:
        return True
    elif 10 in scores and dcard.rank < 10 and dcard.rank > 1:
        return True
    elif 9 in scores and dcard.rank >= 2 and dcard.rank <= 6:
        return True
    return False

def will_double_down_user(self, hand:Hand, the_game) -> bool:
    """Get a double down decision from the user."""
    is_yes = the_game.ui.input('doubledown')
    return is_yes.value


# will_insure functions.
# will_insure functions determine whether the player will buy 
# insurance for a hand. They must accept the following parameters:
#   * self
#   * A cards.Hand object
#   * A game.Game object
# 
# And they must return a bool or a float.
def will_insure_always(self, the_game) -> bool:
    """The player will always buy the most insurance.
    
    :param hand: The hand to make the decision on.
    :param the_game: The information about the current game to use 
        to make a decision.
    :return: A decision whether to double down.
    :rtype: bool
    """
    return the_game.buyin / 2

def will_insure_never(self, the_game) -> bool:
    """The player will never buy insurance.
    
    :param hand: The hand to make the decision on.
    :param the_game: The information about the current game to use 
        to make a decision.
    :return: A decision whether to double down.
    :rtype: bool
    """
    return 0

def will_insure_user(self, the_game) -> bool:
    """Get a insurance decision from the user."""
    is_yes = the_game.ui.input('insure')
    return is_yes.value


def playerfactory(name, will_hit_fn, will_split_fn, will_buyin_fn, 
                  will_double_down, will_insure) -> type:
    """A factory function for Player subclasses."""
    attrs = {
        'will_hit': will_hit_fn,
        'will_split': will_split_fn,
        'will_buyin': will_buyin_fn,
        'will_double_down': will_double_down,
        'will_insure': will_insure,
    }
    return type(name, (Player,), attrs)


# Player subclasses.
Dealer = playerfactory('Dealer', will_hit_dealer, None, None, None, None)
AutoPlayer = playerfactory('AutoPlayer', will_hit_dealer, will_split_always,
                           will_buyin_always, will_double_down_always, 
                           will_insure_always)
BetterPlayer = playerfactory('BetterPlayer', will_hit_recommended, 
                             will_split_recommended, will_buyin_always, 
                             will_double_down_recommended, will_insure_never)
UserPlayer = playerfactory('UserPlayer', will_hit_user, will_split_user, 
                           will_buyin_always, will_double_down_user, 
                           will_insure_user)
