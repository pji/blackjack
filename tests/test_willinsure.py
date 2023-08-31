"""
test_willinsure.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willinsure module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from random import seed

import pytest

from blackjack import model
from blackjack import willinsure as wi
from tests.common import engine, player


# Test cases.
@pytest.mark.will('will_insure', wi.will_insure_always)
def test_will_insure_always(player, engine):
    """When called as the will_insure method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willinsure.will_insure_always`
    should always insure the maximum amount.
    """
    assert player.will_insure(engine) == 10


@pytest.mark.will('will_insure', wi.will_insure_never)
def test_will_insure_never(player, engine):
    """When called as the will_insure method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willinsure.will_insure_never`
    should never insure.
    """
    assert player.will_insure(engine) == 0


@pytest.mark.will('will_insure', wi.will_insure_random)
def test_will_insure_random(player, engine):
    """When called as the will_insure method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willinsure.will_insure_random`
    should randomly insure.
    """
    seed('spam')
    assert player.will_insure(engine) == 1
    assert player.will_insure(engine) == 4
    assert player.will_insure(engine) == 0


@pytest.mark.will('will_insure', wi.will_insure_user)
def test_will_insure_user(player, engine):
    """When called as the will_insure method of a
    :class:`Player` object with a :class:`game.Engine`,
    :func:`willinsure.will_insure_user`
    should prompt the user for a decision.
    """
    engine.ui.insure_prompt.return_value = model.Bet(5)
    assert player.will_insure(engine) == 5
