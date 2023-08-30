"""
test_willdoubledown.py
~~~~~~~~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.test_willdoubledown
module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from functools import partial
from random import seed

import pytest

from blackjack import cards, cli, players, game, model
from blackjack import willdoubledown as wdd
from tests.common import engine, hand, hands, player


# Tests cases.
@pytest.mark.hand([3, 1], [4, 2])
@pytest.mark.will('will_double_down', wdd.will_double_down_always)
def test_will_double_down_always(engine, hand, player):
    """When called as the will_double_down
    method of a :class:`Player` object with a :class:`Hand` and
    a :class:`game.Engine`, :func:`willbet.will_double_down_always`
    will always double down.
    """
    assert player.will_double_down(hand, game)


@pytest.mark.hand([3, 1], [4, 2])
@pytest.mark.will('will_double_down', wdd.will_double_down_never)
def test_will_double_down_never(engine, hand, player):
    """When called as the will_double_down
    method of a :class:`Player` object with
    a :class:`Hand` and
    a :class:`game.Engine`,
    :func:`willbet.will_double_down_never`
    will never double down.
    """
    assert not player.will_double_down(hand, game)


@pytest.mark.hand([3, 1], [4, 2])
@pytest.mark.will('will_double_down', wdd.will_double_down_random)
def test_will_double_down_random(engine, hand, player):
    """When called as the will_double_down
    method of a :class:`Player` object with
    a :class:`Hand` and
    a :class:`game.Engine`,
    :func:`willbet.will_double_down_random`
    will randomly double down.
    """
    seed('spam')
    assert player.will_double_down(hand, engine)
    assert not player.will_double_down(hand, engine)
    assert player.will_double_down(hand, engine)


@pytest.mark.hands(
    [[5, 1], [6, 2]],
    [[4, 0], [6, 0]],
    [[4, 1], [5, 3]],
    [[10, 0], [8, 3]],
    [[6, 2], [10, 2]],
    [[1, 2], [10, 2]],
)
@pytest.mark.will('will_double_down', wdd.will_double_down_recommended)
def test_will_double_down_recommended(engine, hands, player):
    """When called as the will_double_down
    method of a :class:`Player` object with
    a :class:`Hand` and
    a :class:`game.Engine`,
    :func:`willbet.will_double_down_recommended`
    will randomly double down.
    """
    ph11, ph10, ph9, dhand10, dhand7, dhand1 = hands
    engine.dealer.hands = (dhand7,)
    assert player.will_double_down(ph11, engine)
    assert player.will_double_down(ph10, engine)
    assert player.will_double_down(ph9, engine)

    engine.dealer.hands = (dhand10,)
    assert not player.will_double_down(ph10, engine)
    engine.dealer.hands = (dhand1,)
    assert not player.will_double_down(ph10, engine)


@pytest.mark.hand([3, 1], [4, 2])
@pytest.mark.will('will_double_down', wdd.will_double_down_user)
def test_will_double_down_user(engine, hand, player):
    """When called as the will_double_down
    method of a :class:`Player` object with
    a :class:`Hand` and
    a :class:`game.Engine`,
    :func:`willbet.will_double_down_recommended`
    will prompt the user for a choice.
    """
    engine.ui.doubedown_prompt.return_value = True
    assert player.will_double_down(hand, engine)
