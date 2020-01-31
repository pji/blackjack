"""
willbuyin
~~~~~~~~~

The module contains the will_buyin decision functions for players. These 
determine whether the player will hit or stand. They must:

* Accept self
* Accept a game.Engine object
* Return a bool

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from random import choice


# Function.
def will_buyin_always(self, the_game) -> bool:
    """The player will always try to buy into a game.
    
    :param game: The game to buy into.
    :return: Whether to buy into the game.
    :rtype: bool
    """
    return True


def will_buyin_dealer(self, *args):
    """Dealers cannot buyin."""
    msg = 'Dealers cannot buuyin.'
    raise TypeError(msg)


def will_buyin_never(self, the_game) -> bool:
    """Never buyin."""
    return False


def will_buyin_random(self, the_game: 'game.Engine') -> bool:
    """Randomly buyin."""
    return choice([True, False])


# List of valid will_buyin functions.
will_buyins = [
    will_buyin_dealer, 
    will_buyin_always,
    will_buyin_never,
    will_buyin_random,
]
