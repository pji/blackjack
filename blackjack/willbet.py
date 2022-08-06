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


def will_bet_dealer(self, engine: Engine) -> int:
    """The dealer cannot bet."""
    msg = 'Dealer cannot bet.'
    raise TypeError(msg)


def will_bet_max(self, engine: Engine) -> int:
    """The player always bets the maximum amount."""
    if self.chips < engine.bet_max:
        return self.chips
    return engine.bet_max


def will_bet_min(self, engine: Engine) -> int:
    """The player always bets the minimum amount."""
    return engine.bet_min
