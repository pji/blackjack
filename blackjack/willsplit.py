"""
willsplit
~~~~~~~~~

The module contains the will_split decision functions for players.
These functions decide whether a player will split a hand. They
must:

* Accept self
* Accept a cards.Hand object
* Accept a game.Engine object
* Return a bool

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from random import choice
from typing import Callable

from blackjack.cards import Hand


# Functions.
def will_split_always(self, hand: Hand, the_game) -> bool:
    """The player will always split where possible.

    :param hand: The hand that may be split.
    :return: The decision whether to split.
    :rtype: bool
    """
    return True


def will_split_dealer(self, *args):
    """Dealers cannot split."""
    msg = 'Dealers cannot split.'
    raise TypeError(msg)


def will_split_never(self, hand: Hand, the_game) -> bool:
    """Never split."""
    return False


def will_split_random(self, hand: Hand, the_game) -> bool:
    """Split randomly."""
    return choice([True, False])


def will_split_recommended(self, hand: Hand, the_game) -> bool:
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


def will_split_user(self, hand: Hand, the_game) -> bool:
    """Get a split decision from the user."""
#     is_yes = the_game.ui.input('split')
    is_yes = the_game.ui.split_prompt()
    return is_yes.value


# List of valid will_split functions.
# The following must be true to avoid unexpected behavior in randomly
# generated players:
#   * The user version must be at index 0.
#   * The dealer version must be at index 1.
will_splits: list[Callable] = [
    will_split_user,
    will_split_dealer,
    will_split_always,
    will_split_never,
    will_split_random,
    will_split_recommended,
]
