"""
test_willbet.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willbet module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from itertools import cycle
from random import seed

import pytest

from blackjack import model, willbet
from tests.common import engine, player


# Test cases.
@pytest.mark.will('will_bet', willbet.will_bet_count)
def test_will_bet_count(engine, player):
    """When called as the will_bet method of a :class:`Player`
    object with a :class:`game.Engine`, :func:`willbet.will_bet_count`
    will bet based on the running count of the game.
    """
    engine.card_count = 1
    assert player.will_bet(engine) == 100
    engine.card_count = -1
    assert player.will_bet(engine) == 20
    engine.card_count = 0
    assert player.will_bet(engine) == 20
    player.chips = 95
    engine.card_count = 1
    assert player.will_bet(engine) == 95


@pytest.mark.will('will_bet', willbet.will_bet_count_badly)
def test_will_bet_count_badly(mocker, engine, player):
    """When called as the will_bet method of a :class:`Player`
    object with a :class:`game.Engine`,
    :func:`willbet.will_bet_count_badly`
    will bet based on the running count of the game,
    but it will skew the count by a random number each
    time a decision is made.
    """
    mocker.patch('blackjack.willbet.roll', side_effect=cycle([1, 10, 19]))
    engine.card_count = 1
    assert player.will_bet(engine) == 20        # 1
    assert player.will_bet(engine) == 100       # 10
    assert player.will_bet(engine) == 100       # 19
    engine.card_count = -1
    assert player.will_bet(engine) == 20        # 1
    assert player.will_bet(engine) == 20        # 10
    assert player.will_bet(engine) == 100       # 19
    engine.card_count = 0
    assert player.will_bet(engine) == 20        # 1
    assert player.will_bet(engine) == 20        # 10
    assert player.will_bet(engine) == 100       # 19
    player.chips = 95
    engine.card_count = 1
    assert player.will_bet(engine) == 20        # 1
    assert player.will_bet(engine) == 95        # 10
    assert player.will_bet(engine) == 95        # 19


@pytest.mark.will('will_bet', willbet.will_bet_dealer)
def test_will_bet_dealer(mocker, engine, player):
    """When called as the will_bet method of a :class:`Player`
    object with a :class:`game.Engine`, :func:`willbet.will_bet_dealer`
    will raise a :class:`TypeError`.
    """
    with pytest.raises(TypeError, match='Dealer cannot bet[.]'):
        _ = player.will_bet(engine)


@pytest.mark.will('will_bet', willbet.will_bet_max)
def test_will_bet_max(engine, player):
    """When called as the will_bet method of a :class:`Player`
    object with a :class:`game.Engine`, :func:`willbet.will_bet_max`
    will bet the maximum bet.
    """
    assert player.will_bet(engine) == 100
    player.chips = 95
    assert player.will_bet(engine) == 95


@pytest.mark.will('will_bet', willbet.will_bet_min)
def test_will_bet_min(engine, player):
    """When called as the will_bet method of a :class:`Player`
    object with a :class:`game.Engine`, :func:`willbet.will_bet_min`
    will bet the minimum bet.
    """
    assert player.will_bet(engine) == 20


@pytest.mark.will('will_bet', willbet.will_bet_never)
def test_will_bet_never(engine, player):
    """When called as the will_bet method of a :class:`Player`
    object with a :class:`game.Engine`, :func:`willbet.will_bet_never`
    will bet zero.
    """
    assert player.will_bet(engine) == 0


@pytest.mark.will('will_bet', willbet.will_bet_random)
def test_will_bet_random(engine, player):
    """When called as the will_bet method of a :class:`Player`
    object with a :class:`game.Engine`, :func:`willbet.will_bet_random`
    will bet a random amount.
    """
    seed('spam')
    assert player.will_bet(engine) == 35
    assert player.will_bet(engine) == 53
    assert player.will_bet(engine) == 20


@pytest.mark.will('will_bet', willbet.will_bet_user)
def test_will_bet_user(engine, player):
    """When called as the will_bet method of a :class:`Player`
    object with a :class:`game.Engine`, :func:`willbet.will_bet_never`
    will prompt the user for an amount to bet.
    """
    engine.ui.bet_prompt.return_value = model.Bet(50)
    assert player.will_bet(engine) == 50
