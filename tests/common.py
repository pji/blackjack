"""
common
~~~~~~

Common fixtures and utilities for :mod:`blackjack` unit tests.
"""
from types import MethodType

import pytest

from blackjack import cli, cards, players, game


# Utility function.
def get_mark(name, marks):
    by_name = {mark.name: mark for mark in marks}
    if name in by_name:
        return by_name[name]
    return None


# Common fixtures.
@pytest.fixture
def deck(request):
    """Create a :class:`Deck` object for testing."""
    marker = get_mark('deck', request.node.own_markers)
    if marker is not None:
        cardlist = [cards.Card(*args) for args in marker.args]
        return cards.Deck(cardlist)
    return cards.Deck([
        cards.Card(1, 0),
        cards.Card(2, 0),
        cards.Card(3, 0),
    ])


@pytest.fixture
def engine(mocker, request):
    """Create a :class:`Engine` object for testing."""
    marker = get_mark('argv', request.node.own_markers)
    if marker is not None:
        mocker.patch('sys.argv', list(marker.args))
        mocker.patch('blackjack.cards.randrange', return_value=65)
        args = cli.parse_cli()
        return cli.build_game(args)
    mocker.patch(
        'blackjack.game.ValidUI.validate',
        return_value=mocker.Mock()
    )
    return game.Engine(buyin=20, bet_max=100)


@pytest.fixture
def hand(request):
    """Create a :class:`Hand` object for testing."""
    marker = get_mark('hand', request.node.own_markers)
    if marker is not None:
        cardlist = [cards.Card(*args) for args in marker.args]
        return cards.Hand(cardlist)
    return cards.Hand([
        cards.Card(1, 0),
        cards.Card(2, 0),
        cards.Card(3, 0),
    ])


@pytest.fixture
def hands(request):
    """Create a :class:`Hand` object for testing."""
    marker = request.node.get_closest_marker('hands')
    hands = []
    for item in marker.args:
        cardlist = [cards.Card(*args) for args in item]
        hands.append(cards.Hand(cardlist))
    return tuple(hands)


@pytest.fixture
def msgobj(request):
    class Spam:
        msg = '{}'
    return Spam()


@pytest.fixture
def player(request):
    """Create a :class:`AutoPlayer` object for testing."""
    player = players.AutoPlayer(name='Eric', chips=100)
    marker = get_mark('will', request.node.own_markers)
    if not marker:
        return player
    name, meth = marker.args
    if name == 'will_bet':
        player.will_bet = MethodType(meth, player)
    elif name == 'will_double_down':
        player.will_double_down = MethodType(meth, player)
    elif name == 'will_hit':
        player.will_hit = MethodType(meth, player)
    elif name == 'will_insure':
        player.will_insure = MethodType(meth, player)
    elif name == 'will_split':
        player.will_split = MethodType(meth, player)
    player.bet = 20
    return player
