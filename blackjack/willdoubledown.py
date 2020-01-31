"""
willdoubledown
~~~~~~~~~~~~~~

The module contains the will_double_down decision functions for 
players. These determine whether the player will hit or stand. They 
must:

* Accept self
* Accept a cards.Hand object
* Accept a game.Engine object
* Return a bool

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from random import choice

from blackjack.cards import Hand


# Functions.
def will_double_down_always(self, hand:Hand, the_game) -> bool:
    """The player will always double down.
    
    :param hand: The hand to make the decision on.
    :param the_game: The information about the current game to use 
        to make a decision.
    :return: A decision whether to double down.
    :rtype: bool
    """
    return True


def will_double_down_dealer(self, *args):
    """Dealers cannot double down."""
    msg = 'Dealers cannot double down.'
    raise TypeError(msg)


def will_double_down_never(self, hand:Hand, the_game) -> bool:
    """Never double down."""
    return False


def will_double_down_random(self, hand:Hand, the_game: 'game.Engine') -> bool:
    """Randomly double down."""
    return choice([True, False])


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
    is_yes = the_game.ui.doubledown_prompt()
    return is_yes.value


# List of valid will_double_down functions.
# The following must be true to avoid unexpected behavior in randomly 
# generated players:
#   * The user version must be at index 0.
#   * The dealer version must be at index 1.
will_double_downs = [
    will_double_down_user, 
    will_double_down_dealer,
    will_double_down_always, 
    will_double_down_never,
    will_double_down_random,
    will_double_down_recommended,
]
