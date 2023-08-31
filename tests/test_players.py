"""
test_players.py
~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.players module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import json
from functools import partial
from random import seed
from types import MethodType

import pytest

from blackjack import cards, cli, players, game, model
from blackjack import willbet as wb
from blackjack import willdoubledown as wdd
from blackjack import willhit as wh
from blackjack import willinsure as wi
from blackjack import willsplit as ws
from tests.common import hands, msgobj


# Utility functions.
def raises_test(cls, *args, **kwargs):
    """Return the exception raised by the callable."""
    try:
        cls(*args, **kwargs)
    except Exception as ex:
        return type(ex), str(ex)
    return None


def validator_test(fn, self, value):
    try:
        return fn(self, value)
    except Exception as ex:
        return type(ex), str(ex)


# Common fixtures.
@pytest.fixture
def player():
    """A :class:`players.Player` object for testing."""
    player = players.Player((), 'Graham', 100, 0, 0)
    player.will_bet = MethodType(players.willbet.will_bet_max, player)
    player.will_double_down = MethodType(
        players.wdd.will_double_down_always,
        player
    )
    player.will_hit = MethodType(players.wh.will_hit_dealer, player)
    player.will_insure = MethodType(
        players.wi.will_insure_always,
        player
    )
    player.will_split = MethodType(players.ws.will_split_always, player)
    return player


# Tests for Player class methods.
def test_Player_deserialize(player):
    """Given a :class:`Player` object serialized as a JSON string,
    :meth:`Player.serialize` should return the deserialized object.
    """
    serial = player.serialize()
    assert players.Player.deserialize(serial) == player


def test_Player_deserialize_invalid(player):
    """Given a :class:`Player` object serialized as a JSON string,
    :meth:`Player.serialize` should return the deserialized object.
    If the `will_*` method names are not valid, raise a ValueError.
    """
    pdict = player._asdict()
    for key in [k for k in pdict if k.startswith('will_')]:
        bad_dict = pdict.copy()
        bad_dict[key] = 'spam'
        serial = json.dumps(bad_dict)
        with pytest.raises(ValueError):
            _ = players.Player.deserialize(serial)


# Tests for Player initialization.
def test_Player_all_default():
    """Given no values, :class:`Player` object's attributes should be
    set to default values.
    """
    optionals = {
        'hands': (),
        'name': 'Player',
        'chips': 0,
        'insured': 0,
    }
    obj = players.Player()
    for attr in optionals:
        assert getattr(obj, attr) == optionals[attr]


def test_Player_init_all_invalid():
    """Given invalid values, :class:`Player` should raise the appropriate
    exception.
    """
    raises = partial(raises_test, players.Player)
    assert raises('spam') == (ValueError, 'Invalid (contains non-hand).')
    assert raises(name=b'Montr\xe9al') == (
        ValueError, 'Invalid text (contains invalid unicode characters).'
    )
    assert raises(chips='spam') == (
        ValueError, 'Invalid integer (cannot be made an integer).'
    )
    assert raises(insured=-3) == (
        ValueError, 'Invalid (cannot be less than 0).'
    )
    assert raises(bet=-3) == (
        ValueError, 'Invalid (cannot be less than 0).'
    )


@pytest.mark.hands([[1, 3], [11, 3]], [[2, 0], [3, 1]])
def test_Player_all_optionals(hands):
    """Given no values, :class:`Player` object's attributes should be
    set to default values.
    """
    optionals = {
        'hands': hands,
        'name': 'Spam',
        'chips': 100,
        'insured': 20,
    }
    obj = players.Player(**optionals)
    for attr in optionals:
        assert getattr(obj, attr) == optionals[attr]


# Tests for Player dunder methods.
def test_Player_format(player):
    """When invoked, :meth:`Player.__format__` should return as though
    it was called on the value of the name attribute.
    """
    assert f'{player:<10}' == 'Graham    '


def test_Player_str(player):
    """:meth:`Player.__str__` should return the name of the object."""
    assert str(player) == 'Graham'


# Tests for Player private methods.
@pytest.mark.hands([[1, 3], [11, 3]], [[2, 0], [3, 1]])
def test_Player__asdict(player, hands):
    """When called, :meth:`Player._asdict() should serialize the object
    to a :class:`dict`.
    """
    player.hands = hands
    assert player._asdict() == {
        'class': 'Player',
        'chips': 100,
        'hands': hands,
        'insured': 0,
        'name': 'Graham',
        'will_bet': 'will_bet_max',
        'will_double_down': 'will_double_down_always',
        'will_hit': 'will_hit_dealer',
        'will_insure': 'will_insure_always',
        'will_split': 'will_split_always',
    }


# Tests for Player public methods.
@pytest.mark.hands([[1, 3], [11, 3]], [[2, 0], [3, 1]])
def test_Player_serialize(player, hands):
    """When called, :meth:`Player.serialize` should return the object
    serialized as a JSON string.
    """
    player.hands = hands
    assert player.serialize() == json.dumps({
        'class': 'Player',
        'chips': 100,
        'hands': tuple(h.serialize() for h in hands),
        'insured': 0,
        'name': 'Graham',
        'will_bet': 'will_bet_max',
        'will_double_down': 'will_double_down_always',
        'will_hit': 'will_hit_dealer',
        'will_insure': 'will_insure_always',
        'will_split': 'will_split_always',
    })


# Tests for playerfactory.
def test_playerfactory_populates_methods():
    """Given a `will_*` function, :func:`playerfactory` should
    return a :class:`Player` subclass with the given method.
    """
    def bet(self, game):
        pass

    def double_down(self, game):
        pass

    def hit(self, hand):
        pass

    def insure(self, hand):
        pass

    def split(self, hand, game):
        pass

    Eggs = players.playerfactory(
        'Spam',
        will_bet=bet,
        will_double_down=double_down,
        will_hit=hit,
        will_insure=insure,
        will_split=split
    )
    assert Eggs.__name__ == 'Spam'
    assert Eggs.will_bet is bet
    assert Eggs.will_double_down is double_down
    assert Eggs.will_hit is hit
    assert Eggs.will_insure is insure
    assert Eggs.will_split is split


# Tests for make_player.
def test_make_player():
    """When invoked, :func:`make_player` should return a randomly
    created :class:`Player` object.
    """
    seed('spam')
    p1 = players.make_player()._asdict()
    p2 = players.make_player()._asdict()
    assert p1['name'] == 'Andrew'
    assert p1['chips'] == 200
    assert p1['will_bet'] == 'will_bet_random'
    assert p1['will_double_down'] == 'will_double_down_recommended'
    assert p1['will_hit'] == 'will_hit_never'
    assert p1['will_insure'] == 'will_insure_random'
    assert p1['will_split'] == 'will_split_random'
    assert p2['name'] == 'Daren'
    assert p1['chips'] == 200
    assert p2['will_bet'] == 'will_bet_random'
    assert p2['will_double_down'] == 'will_double_down_recommended'
    assert p2['will_hit'] == 'will_hit_random'
    assert p2['will_insure'] == 'will_insure_always'
    assert p2['will_split'] == 'will_split_recommended'


def test_make_player_random_chips():
    """Given a bet, :func:`make_player` should return a random number
    of chips based on that bet.
    """
    seed('spam')
    p1 = players.make_player(bet=10)
    p2 = players.make_player(bet=10)
    p3 = players.make_player(bet=10)
    assert p1.chips == 40
    assert p2.chips == 190
    assert p3.chips == 80


# Tests for get_chips.
def test_get_chips():
    """Given a buy-in value, :func:`get_chips` should return a number
    of chips that is between 1 and 21 times the given buy-in.
    """
    seed('spam')
    assert players.get_chips(10) == 40
    assert players.get_chips(10) == 90
    assert players.get_chips(10) == 10


# Tests for validators.
def test_validate_player_or_none(msgobj, player):
    """:func:`validate_player_or_none` should accept :class:`Player`
    objects or `None`.
    """
    accepts = partial(validator_test, players.validate_player_or_none, msgobj)
    assert accepts(player) == player
    assert accepts(player.serialize()) == player
    assert accepts(None) is None
    assert accepts(0) == (ValueError, 'not an instance of Player')
