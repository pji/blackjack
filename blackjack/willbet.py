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
from blackjack.game import Engine


def will_bet_max(self, engine: Engine) -> int:
    """The player always bets the maximum amount."""
    return engine.bet_max
