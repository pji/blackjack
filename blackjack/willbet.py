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
from random import randrange
from typing import Callable

from yadr import roll

from blackjack.model import BaseEngine


def will_bet_count(self, engine: BaseEngine) -> int:
    """The player bets max when count is positive and min when the
    count is not.
    """
    bet = engine.bet_min
    if engine.card_count > 0:
        bet = engine.bet_max
    if bet > self.chips:
        bet = self.chips
    return bet


def will_bet_count_badly(self, engine: BaseEngine) -> int:
    """The player bets max when count is positive and min when the
    count is not.
    """
    miscount = roll('1d19')
    if not isinstance(miscount, int):
        msg = f'Type needs to be int. Was: {type(miscount).__name__}'
        raise ValueError(msg)
    head_count = engine.card_count + miscount - 10
    bet = engine.bet_min
    if head_count > 0:
        bet = engine.bet_max
    if bet > self.chips:
        bet = self.chips
    return bet


def will_bet_dealer(self, engine: BaseEngine) -> int:
    """The dealer cannot bet."""
    msg = 'Dealer cannot bet.'
    raise TypeError(msg)


def will_bet_max(self, engine: BaseEngine) -> int:
    """The player always bets the maximum amount."""
    if self.chips < engine.bet_max:
        return self.chips
    return engine.bet_max


def will_bet_min(self, engine: BaseEngine) -> int:
    """The player always bets the minimum amount."""
    return engine.bet_min


def will_bet_never(self, engine: BaseEngine) -> int:
    """The player always bets the minimum amount."""
    return 0


def will_bet_random(self, engine: BaseEngine) -> int:
    """The player always bets the minimum amount."""
    return randrange(engine.bet_min, engine.bet_max)


def will_bet_user(self, engine: BaseEngine) -> int:
    """Player prompts user for bet."""
    bet = engine.ui.bet_prompt(engine.bet_min, engine.bet_max)
    return bet.value


# List of valid will_bet functions.
will_bets: list[Callable] = [
    # Functions for special players.
    will_bet_dealer,
    will_bet_user,

    # Functions safe for random players.
    will_bet_count,
    will_bet_count_badly,
    will_bet_max,
    will_bet_min,
    will_bet_never,
    will_bet_random,
]
