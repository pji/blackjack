"""
testwh.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willhit module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from random import seed

import pytest

from blackjack import model
from blackjack import willhit as wh
from tests.common import engine, hand, hands, player


# Test cases.
@pytest.mark.hands(
    [[3, 1], [4, 2]],
    [[7, 1], [10, 2]],
    [[10, 3], [6, 3], [11, 3]],
)
@pytest.mark.will('will_hit', wh.will_hit_dealer)
def test_will_hit_dealer(hands, player, engine):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_dealer`
    should hit while the hand is under 16
    then stand.
    """
    hand7, hand17, handbust = hands
    assert player.will_hit(hand7, engine)


@pytest.mark.hand([6, 2], [7, 3])
@pytest.mark.will('will_hit', wh.will_hit_never)
def test_will_hit_never(hand, player, engine):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_never`
    should never hit.
    """
    assert not player.will_hit(hand, engine)


@pytest.mark.hand([6, 2], [7, 3])
@pytest.mark.will('will_hit', wh.will_hit_random)
def test_will_hit_random(hand, player, engine):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_never`
    should randomly hit.
    """
    seed('spam')
    assert player.will_hit(hand, engine)
    assert not player.will_hit(hand, engine)
    assert player.will_hit(hand, engine)


@pytest.mark.hands(
    [[3, 1], [4, 2]],
    [[7, 1], [10, 2]],
)
@pytest.mark.will('will_hit', wh.will_hit_recommended)
def test_will_hit_recommended_dealer_7_plus(hands, player, engine):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_recommended`
    should hit while the hand is under 17
    if the dealer is showing a 7–11.
    """
    phand, dhand = hands
    engine.dealer.hands = (dhand,)
    assert player.will_hit(phand, engine)


@pytest.mark.hands(
    [[5, 1], [7, 2]],
    [[3, 1], [10, 2]],
)
@pytest.mark.will('will_hit', wh.will_hit_recommended)
def test_will_hit_recommended_play_12_dealer_3_minus(hands, player, engine):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_recommended`
    should hit if the player has less than 13
    and the dealer is showing 2–3
    """
    phand, dhand = hands
    engine.dealer.hands = (dhand,)
    assert player.will_hit(phand, engine)


@pytest.mark.hands(
    [[4, 1], [7, 2]],
    [[5, 1], [10, 2]],
)
@pytest.mark.will('will_hit', wh.will_hit_recommended)
def test_will_hit_recommended_play_12_dealer_3_minus(hands, player, engine):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_recommended`
    should hit if the player has less than 12
    and the dealer is showing 4–6
    """
    phand, dhand = hands
    engine.dealer.hands = (dhand,)
    assert player.will_hit(phand, engine)


@pytest.mark.hands(
    [[1, 1], [7, 2]],
    [[3, 1], [10, 2]],
)
@pytest.mark.will('will_hit', wh.will_hit_recommended)
def test_will_hit_recommended_soft_18(hands, player, engine):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_recommended`
    should hit if the player has less than 19
    and the player has an ace.
    """
    phand, dhand = hands
    engine.dealer.hands = (dhand,)
    assert player.will_hit(phand, engine)


@pytest.mark.hands(
    [[1, 1], [8, 2]],
    [[3, 1], [10, 2]],
)
@pytest.mark.will('will_hit', wh.will_hit_recommended)
def test_will_hit_recommended_soft_19(hands, player, engine):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_recommended`
    should stand if the player has 19 or more
    and the player has an ace.
    """
    phand, dhand = hands
    engine.dealer.hands = (dhand,)
    assert not player.will_hit(phand, engine)


@pytest.mark.hands(
    [[10, 1], [11, 2]],
    [[5, 1], [10, 2]],
)
@pytest.mark.will('will_hit', wh.will_hit_recommended)
def test_will_hit_recommended_default(hands, player, engine):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_recommended`
    should default to standing.
    """
    phand, dhand = hands
    engine.dealer.hands = (dhand,)
    assert not player.will_hit(phand, engine)


@pytest.mark.hands(
    [[10, 1], [11, 2], [5, 0]],
    [[5, 1], [10, 2]],
)
@pytest.mark.will('will_hit', wh.will_hit_recommended)
def test_will_hit_recommended_default(hands, player, engine):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_recommended`
    should stand if the player is bust.
    """
    phand, dhand = hands
    engine.dealer.hands = (dhand,)
    assert not player.will_hit(phand, engine)


@pytest.mark.hand([3, 1], [4, 2])
@pytest.mark.will('will_hit', wh.will_hit_user)
def test_will_hit_user(engine, hand, player):
    """When called as the will_hit method of a
    :class:`Player` object with a :class:`Hand`
    and a :class:`game.Engine`,
    :func:`willhit.will_hit_user`
    should prompt the user for a decision.
    """
    engine.ui.hit_prompt.return_value = model.IsYes('y')
    assert player.will_hit(hand, engine)
