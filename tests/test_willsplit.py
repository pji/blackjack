"""
test_willsplit.py
~~~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willsplit module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from random import seed

import pytest

from blackjack import model
from blackjack import willsplit as ws
from tests.common import engine, hand, hands, player


# Test case.
@pytest.mark.hand([5, 1], [5, 3])
@pytest.mark.will('will_split', ws.will_split_always)
def test_will_split_always(hand, engine, player):
    """When called as the will_split method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willsplit.will_split_always`
    should always split.
    """
    assert player.will_split(hand, engine)


@pytest.mark.hand([5, 1], [5, 3])
@pytest.mark.will('will_split', ws.will_split_never)
def test_will_split_never(hand, engine, player):
    """When called as the will_split method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willsplit.will_split_never`
    should never split.
    """
    assert not player.will_split(hand, engine)


@pytest.mark.hand([5, 1], [5, 3])
@pytest.mark.will('will_split', ws.will_split_random)
def test_will_split_random(hand, engine, player):
    """When called as the will_split method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willsplit.will_split_random`
    should randomly split.
    """
    seed('spam')
    assert player.will_split(hand, engine)
    assert not player.will_split(hand, engine)
    assert player.will_split(hand, engine)


@pytest.mark.hands(
    [[1, 1], [1, 3]],
    [[8, 1], [8, 3]],
    [[7, 3], [10, 0]],
)
@pytest.mark.will('will_split', ws.will_split_recommended)
def test_will_split_recommended_aces_and_8(hands, engine, player):
    """When called as the will_split method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willsplit.will_split_recommended`
    should always split aces and eights.
    """
    phand1, phand8, dhand = hands
    engine.dealer.hands = (dhand,)
    assert player.will_split(phand1, engine)
    assert player.will_split(phand8, engine)


@pytest.mark.hands(
    [[4, 1], [4, 3]],
    [[5, 1], [5, 3]],
    [[11, 1], [11, 3]],
    [[7, 3], [10, 0]],
)
@pytest.mark.will('will_split', ws.will_split_recommended)
def test_will_split_recommended_4_5_10(hands, engine, player):
    """When called as the will_split method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willsplit.will_split_recommended`
    should never split fours, fives, and tens.
    """
    phand4, phand5, phand10, dhand = hands
    engine.dealer.hands = (dhand,)
    assert not player.will_split(phand4, engine)
    assert not player.will_split(phand5, engine)
    assert not player.will_split(phand10, engine)


@pytest.mark.hands(
    [[2, 1], [2, 3]],
    [[3, 1], [3, 3]],
    [[7, 1], [7, 3]],
    [[7, 3], [10, 0]],
    [[8, 3], [10, 0]],
)
@pytest.mark.will('will_split', ws.will_split_recommended)
def test_will_split_recommended_2_3_7(hands, engine, player):
    """When called as the will_split method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willsplit.will_split_recommended`
    should split twos, threes, and sevens if the dealer
    is showing a seven or less. Otherwise don't split.
    """
    phand2, phand3, phand7, dhand7, dhand8 = hands
    engine.dealer.hands = (dhand7,)
    assert player.will_split(phand2, engine)
    assert player.will_split(phand3, engine)
    assert player.will_split(phand7, engine)

    engine.dealer.hands = (dhand8,)
    assert not player.will_split(phand2, engine)
    assert not player.will_split(phand3, engine)
    assert not player.will_split(phand7, engine)


@pytest.mark.hands(
    [[6, 1], [6, 3]],
    [[6, 3], [10, 0]],
    [[7, 3], [10, 0]],
)
@pytest.mark.will('will_split', ws.will_split_recommended)
def test_will_split_recommended_6(hands, engine, player):
    """When called as the will_split method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willsplit.will_split_recommended`
    should split sixes if the dealer
    is showing a six or less. Otherwise don't split.
    """
    phand, dhand6, dhand7 = hands
    engine.dealer.hands = (dhand6,)
    assert player.will_split(phand, engine)

    engine.dealer.hands = (dhand7,)
    assert not player.will_split(phand, engine)


@pytest.mark.hand([5, 1], [5, 3])
@pytest.mark.will('will_split', ws.will_split_user)
def test_will_split_user(hand, engine, player):
    """When called as the will_split method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willsplit.will_split_user`
    should prompt the user for a decision.
    """
    engine.ui.split_prompt.return_value = model.IsYes('y')
    assert player.will_split(hand, engine)
