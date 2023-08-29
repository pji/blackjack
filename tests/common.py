"""
common
~~~~~~

Common fixtures and utilities for :mod:`blackjack` unit tests.
"""
from types import MethodType

import pytest

from blackjack import cards, players, game


# Common fixtures.
@pytest.fixture
def engine(mocker):
    """Create a :class:`Engine` object for testing."""
    mocker.patch(
        'blackjack.game.ValidUI.validate',
        return_value=mocker.Mock()
    )
    return game.Engine(buyin=20, bet_max=100)


@pytest.fixture
def hand(request):
    """Create a :class:`Hand` object for testing."""
    marker = request.node.get_closest_marker('hand')
    cardlist = [cards.Card(*args) for args in marker.args]
    yield cards.Hand(cardlist)


@pytest.fixture
def player(request):
    """Create a :class:`AutoPlayer` object for testing."""
    marker = request.node.get_closest_marker('will')
    name, meth = marker.args
    player = players.AutoPlayer(name='Eric', chips=100)
    if name == 'will_bet':
        player.will_bet = MethodType(meth, player)
    elif name == 'will_double_down':
        player.will_double_down = MethodType(meth, player)
    elif nane == 'will_hit':
        player.will_hit = MethodType(meth, player)
    elif name == 'will_insure':
        player.will_insure == MethodType(meth, player)
    elif name == 'will_split':
        player.will_split == MethodType(meth, player)
    return player
