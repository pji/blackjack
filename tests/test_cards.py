"""
test_cards.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.cards module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import collections.abc as col
import json
from copy import deepcopy
from functools import partial
from itertools import chain
from random import seed

import pytest

from blackjack import cards


# Utility functions.
def raises_test(cls, *args, **kwargs):
    """Return the exception raised by the callable."""
    try:
        cls(*args, **kwargs)
    except Exception as ex:
        return type(ex)
    return None


# Tests for Card.
@pytest.fixture
def card():
    """An instance of :class:`blackjack.cards.Card` for testing."""
    yield cards.Card(10, 'clubs', cards.UP)


# Tests for Card class methods.
def test_deserialize(card):
    """When given a :class:`blackjack.cards.Card` object serialized as
    a json string, :meth:`blackjack.cards.Card.deserialize()`` should
    return the deserialized object.
    """
    s = '["Card", 10, "clubs", true]'
    assert cards.Card.deserialize(s) == card


# Tests for Card initialization.
def test_Card__init_default():
    """When invoked, an :class:`blackjack.cards.Card` object is created."""
    optionals = {
        'rank': 11,
        'suit': 'spades',
        'facing': cards.UP,
    }
    card = cards.Card()
    for attr in optionals:
        assert getattr(card, attr) == optionals[attr]


def test_Card__init_invalid():
    """When invoked, an :class:`blackjack.cards.Card` object is created.
    If invalid values for optional parameters are passed, the object
    should raise a :class:`ValueError` exception.
    """
    raises = partial(raises_test, cards.Card)
    assert raises(23, 'clubs', True) == ValueError
    assert raises(0, 'clubs', True) == ValueError
    assert raises(2, 'spam', True) == ValueError
    assert raises(2, 5, True) == ValueError
    assert raises(2, -7, True) == ValueError
    assert raises(2, 'clubs', 'spam') == ValueError


def test_Card__init_optional():
    """When invoked, an :class:`blackjack.cards.Card` object is created.
    If optional parameters are passed, the relevant attributes are set
    to those values.
    """
    optionals = {
        'rank': 10,
        'suit': 'hearts',
        'facing': cards.DOWN,
    }
    card = cards.Card(**optionals)
    for attr in optionals:
        assert getattr(card, attr) == optionals[attr]


# Tests for Card dunder methods.
def test_Card___repr__(card):
    """:class:`blackjack.cards.Card.__repr__` should return a string
    useful for debugging.
    """
    assert repr(card) == "Card(rank=10, suit='clubs', facing=True)"


def test_Card___str__(card):
    """:class:`blackjack.cards.Card.__str__` should return a string
    useful for printing.
    """
    assert str(card) == '10♣︎'


def test_Card___str__(card):
    """:class:`blackjack.cards.Card.__str__` should return a string
    useful for printing. If the card is face down, the suit and rank
    information should be hidden.
    """
    card.facing = cards.DOWN
    assert str(card) == '\u2500\u2500'


def test_Card_comparisons(card):
    """:class:`blackjack.cards.Card` objects should be compared for
    equality based on their rank and suit.
    """
    assert card == cards.Card(10, 'clubs', cards.UP)
    assert card == cards.Card(10, 'clubs', cards.DOWN)
    assert card != cards.Card(11, 'clubs')
    assert card != cards.Card(10, 'hearts')
    assert card != cards.Card(9, 'diamonds')
    assert card < cards.Card(11, 'clubs')
    assert card <= cards.Card(12, 'clubs')
    assert card < cards.Card(10, 'diamonds')
    assert card <= cards.Card(10, 'diamonds')
    assert card > cards.Card(9, 'clubs')
    assert card >= cards.Card(9, 'clubs')
    assert cards.Card(10, 'diamonds') > card
    assert cards.Card(10, 'diamonds') >= card
    assert card.__eq__(23) == NotImplemented


# Tests for Card._astuple.
def test_Card__astuple(card):
    """When called, :meth:`blackjack.cards.Card._astuple` should return
    the card's attributes as a tuple for serialization.
    """
    assert card._astuple() == ('Card', 10, 'clubs', True)


# Tests for Card.flip.
def test_Card_flip_up(card):
    """When a :class:`blackjack.cards.Card` object is face down,
    :meth:`blackjack.cards.Card.flip` should switch it to
    being face up. If the object is face down, it should switch
    it to face up.
    """
    card.flip()
    assert card.facing == cards.DOWN
    card.flip()
    assert card.facing == cards.UP


# Tests for Card.serialize.
def test_Card_serialize(card):
    """When called, :meth:`blackjack.cards.Card.serialize` returns a
    version of the object serialized to a json string.
    """
    assert card.serialize() == '["Card", 10, "clubs", true]'


# Tests for Pile.
# Pile fixtures.
@pytest.fixture
def pile():
    """A :class:`blackjack.cards.Pile` for testing."""
    yield cards.Pile([
        cards.Card(1, 0),
        cards.Card(2, 0),
        cards.Card(3, 0),
    ])


# Tests for Pile class methods.
def test_Pile_deserialize(pile):
    """When given a :class:`blackjack.cards.Pile` object serialized
    to a JSON string, :meth:`blackjack.cards.Pile.deserialize` should
    deserialize that object and return it.
    """
    s = json.dumps({'class': 'Pile', '_iter_index': 0, 'cards': [
        '["Card", 1, 0, true]',
        '["Card", 2, 0, true]',
        '["Card", 3, 0, true]',
    ],})
    assert cards.Pile.deserialize(s) == pile


# Tests for Pile initialization.
def test_Pile_init_default():
    """Given no parameters, :class:`blackjack.cards.Pile` should
    return a instance that uses default values for its attributes.
    """
    optionals = {
        'cards': (),
        '_iter_index': 0
    }
    pile = cards.Pile()
    for attr in optionals:
        assert getattr(pile, attr) == optionals[attr]


def test_Pile_init_invalid():
    """Given an invalid parameter, :class:`Pile` should raise an
    exception.
    """
    raises = partial(raises_test, cards.Pile)
    assert raises('spam') == ValueError
    assert raises(6) == ValueError
    assert raises(['spam', 'eggs']) == ValueError
    assert raises(_iter_index='spam') == ValueError


def test_Pile_init_optional():
    """Given optional parameters, :class:`blackjack.cards.Pile` should
    return a instance that uses the given values for its attributes.
    """
    optionals = {
        'cards': (
            cards.Card(1, 0),
            cards.Card(2, 0),
            cards.Card(3, 0),
        ),
        '_iter_index': 2
    }
    pile = cards.Pile(**optionals)
    for attr in optionals:
        assert getattr(pile, attr) == optionals[attr]


# Tests for Pile dunder methods.
def test_Pile_comparisons(pile):
    """:class:`blackjack.cards.Pile` should be able to be compared with
    other instances of :class:`blackjack.cards.Pile`. The comparison
    should be based on the contents of :attr:`blackjack.cards.Pile.cards`.
    """
    assert pile == cards.Pile(pile.cards)
    assert pile != cards.Pile([cards.Card(1, 0),])
    assert pile.__eq__(23) == NotImplemented


def test_Pile_container(pile):
    """:class:`blackjack.cards.Pile` should implement the `Container`
    protocol.
    """
    assert isinstance(pile, col.Container)
    assert cards.Card(2, 0) in pile
    assert cards.Card(4, 0) not in pile


def test_Pile_iterator(pile):
    """:class:`blackjack.cards.Pile` should implement the iterator
    protocol.
    """
    assert isinstance(pile, col.Iterator)
    assert iter(pile) == pile
    assert iter(pile) is not pile
    next(pile)
    assert pile._iter_index == 1
    assert next(pile) == cards.Card(2, 0)
    assert next(pile) == cards.Card(3, 0)
    with pytest.raises(StopIteration):
        next(pile)


def test_Pile_mutablesequence(pile):
    """:class:`blackjack.cards.Pile` should implement the
    `MutableSequence` protocol.
    """
    assert isinstance(pile, col.MutableSequence)
    card = cards.Card(5, 2)

    # Test Pile.__set_item__.
    assert pile[1] is not card
    pile[1] = card
    assert pile[1] is card

    # Test Pile.__del_item__.
    assert len(pile) == 3
    del pile[1]
    assert pile[1] is not card
    assert len(pile) == 2

    # Test Pile.insert.
    pile.insert(1, card)
    assert pile[1] is card
    assert len(pile) == 3


def test_Pile_reversible(pile):
    """:class:`blackjack.cards.Pile` should implement the `Reversible`
    protocol.
    """
    assert isinstance(pile, col.Reversible)
    assert reversed(pile) == cards.Pile(pile.cards[::-1])


def test_Pile_sequence(pile):
    """:class:`blackjack.cards.Pile` should implement the `Sequence`
    protocol.
    """
    assert isinstance(pile, col.Sequence)
    assert pile[1] == cards.Card(2, 0)


def test_Pile_sized(pile):
    """Pile should implement the `Sized` protocol."""
    assert len(pile) == 3


# Tests for Pile.append.
def test_Pile_append(pile):
    """Given a :class:`Card`, :meth:`Pile.append` should add the card
    to the :class:`Pile`.
    """
    card = cards.Card(4, 0)
    assert len(pile) == 3
    assert pile[-1] == cards.Card(3, 0)
    pile.append(card)
    assert len(pile) == 4
    assert pile[-1] == card


# Tests for Pile.copy.
def test_Pile_copy(pile):
    """When called, :meth:`blackjack.cards.Pile.copy` should return
    a shallow copy of the object.
    """
    result = pile.copy()
    assert pile == result
    assert pile is not result


# Tests for Pile.serialize.
def test_Pile_serialize(pile):
    """When called, :meth:`blackjack.cards.Pile.serialize` should return
    the Pile object serialized to a JSON string.
    """
    assert pile.serialize() == json.dumps({
        'class': 'Pile',
        '_iter_index': 0,
        'cards': [
            '["Card", 1, "clubs", true]',
            '["Card", 2, "clubs", true]',
            '["Card", 3, "clubs", true]',
        ]
    })


# Tests for Deck.
# Fixtures for Deck.
@pytest.fixture
def deck():
    """A :class:`blackjack.cards.Deck` object for testing."""
    yield cards.Deck([
        cards.Card(1, 0),
        cards.Card(2, 0),
        cards.Card(3, 0),
    ])


@pytest.fixture
def frenchdeck():
    cards_ = []
    for suit in range(4):
        for rank in range(13, 0, -1):
            cards_.append(cards.Card(rank, suit, cards.DOWN))
    yield cards.Deck(cards_)


# Tests for Deck class methods and traits.
def test_Deck_subclasses_pile(deck):
    """:class:`blackjack.cards.Deck` should be a subclass of
    :class:`blackjack.cards.Pile`.
    """
    assert isinstance(deck, cards.Pile)


def test_Deck_build(frenchdeck):
    """:meth:`blackjack.cards.Deck.build1 should return an instance
    of :class:`blackjack.cards.Deck` that contains the cards needed
    for a blackjack game.
    """
    deck = cards.Deck.build()
    assert deck == frenchdeck
    assert deck.size == 1


def test_Deck_build_casino_deck(frenchdeck):
    """:meth:`blackjack.cards.Deck.build1 should return an instance
    of :class:`blackjack.cards.Deck` that contains the cards needed
    for a blackjack game. Despite using multiple decks, each card
    in the casino deck should be a unique object.
    """
    deck = cards.Deck.build(6)
    assert deck == cards.Deck(chain(*[frenchdeck for _ in range(6)]))
    assert deck.size == 6
    for i in range(52):
        for j in range(1, 6):
            assert deck[i] is not deck[52 * j + i]
            assert deck[i] == deck[52 * j + i]


def test_Deck_deserialize(deck):
    """When given a Deck serialized as a JSON string, deserialize()
    should return the deserialized Deck object.
    """
    s = json.dumps({'class': 'Deck', '_iter_index': 0, 'size': 1, 'cards': [
        '["Card", 1, 0, true]',
        '["Card", 2, 0, true]',
        '["Card", 3, 0, true]',
    ],})
    assert cards.Deck.deserialize(s) == deck


# Tests for Deck initialization.
def test_Deck_init_default():
    """If no parameters are passed, a :class:`blackjack.cards.Deck`
    object should be initialized with default values.
    """
    optionals = {
        'cards': tuple(),
        'size': 1,
        '_iter_index': 0
    }
    deck = cards.Deck()
    for attr in optionals:
        assert getattr(deck, attr) == optionals[attr]


def test_Deck_invalid():
    """Given an invalid parameter value, :class:`Deck` should raise
    the appropriate exception.
    """
    raises = partial(raises_test, cards.Deck)
    assert raises(size='spam') == ValueError
    assert raises(size=-2) == ValueError
    assert raises(size=['spam', 'eggs']) == TypeError


def test_Deck_init_optionals():
    """If optional parameters are passed, a :class:`blackjack.cards.Deck`
    object should be initialized with those values.
    """
    optionals = {
        'cards': (cards.Card(1, 0), cards.Card(2, 0),),
        'size': 2,
        '_iter_index': 1
    }
    deck = cards.Deck(**optionals)
    for attr in optionals:
        assert getattr(deck, attr) == optionals[attr]


# Tests for Deck.draw.
def test_Deck_draw(deck):
    """When called, :meth:`blackjack.cards.Deck.draw` should remove the
    "top card" of the deck and return it. For performance reasons, "top
    card" is defined as the card at index -1.
    """
    assert len(deck) == 3
    assert deck.draw() == cards.Card(3, 0)
    assert len(deck) == 2


# Tests for Deck.shuffle.
def test_Deck_shuffle(deck):
    """When called, :meth:`blackjack.cards.Deck.shuffle` should
    randomize the order of the deck.
    """
    seed('spam1')
    deck.shuffle()
    assert deck == cards.Deck([
        cards.Card(1, 0),
        cards.Card(3, 0),
        cards.Card(2, 0),
    ])


# Tests for Deck.random_cut.
def test_Deck_random_cut(frenchdeck):
    """When called, :meth:`blackjack.cards.Deck.random_cut` should
    remove between 60 and 75 cards from the deck.
    """
    casinodeck = cards.Deck(chain(*[frenchdeck for _ in range(6)]))
    seed('spam')
    for start in [63, 68, 60, 70]:
        deck = deepcopy(casinodeck)
        deck.random_cut()
        assert deck == casinodeck[start:]


# Tests for Deck.serialize.
def test_Deck_serialize(deck):
    """When called, :meth:`blackjack.cards.Deck.serialize` should return
    the Deck object serialized as a JSON string.
    """
    assert deck.serialize() == json.dumps({
        'class': 'Deck',
        '_iter_index': 0,
        'cards': [
            '["Card", 1, "clubs", true]',
            '["Card", 2, "clubs", true]',
            '["Card", 3, "clubs", true]',
        ],
        'size': 1,
    })


# Tests for Hand.
# Fixtures for Hand.
@pytest.fixture
def blackjack():
    """A :class:`Hand` object with natural blackjack for testing."""
    yield cards.Hand([
        cards.Card(1, 0),
        cards.Card(11, 0),
    ])


@pytest.fixture
def hand():
    """A :class:`Hand` object for testing."""
    yield cards.Hand([
        cards.Card(1, 0),
        cards.Card(2, 0),
        cards.Card(3, 0),
    ])


@pytest.fixture
def hand_20():
    """A :class:`Hand` object with a score of 20 for testing."""
    yield cards.Hand([
        cards.Card(11, 0),
        cards.Card(11, 1),
    ])


@pytest.fixture
def hand_21():
    """A :class:`Hand` object with a score of 21 for testing."""
    yield cards.Hand([
        cards.Card(10, 0),
        cards.Card(7, 0),
        cards.Card(4, 0),
    ])


# Tests for Hand class methods and traits.
def test_Hand_subclasses_Pile(hand):
    """:class:`Hand` should be a subclass of :class:`Pile`."""
    assert isinstance(hand, cards.Pile)


def test_Hand_deserialize(hand):
    """When given a :class:`Hand` serialized as a JSON string,
    :meth:`Hand.deserialize` should return the deserialized
    :class:`Deck` object.
    """
    s = json.dumps({
        'class': 'Hand',
        '_iter_index': 0,
        'doubled_down': False,
        'cards': [
            '["Card", 1, 0, true]',
            '["Card", 2, 0, true]',
            '["Card", 3, 0, true]',
        ],
    })
    assert cards.Hand.deserialize(s) == hand


# Tests for Hand initialization.
def test_Hand_init_default():
    """Given no parameters, :class:`blackjack.cards.Hand` should
    return a instance that uses default values for its attributes.
    """
    optionals = {
        'cards': (),
        '_iter_index': 0,
        'doubled_down': False,
    }
    hand = cards.Hand()
    for attr in optionals:
        assert getattr(hand, attr) == optionals[attr]


def test_Hand_init_invalid():
    """Given an invalid parameter value, :class:`Hand` should raise
    the appropriate exception.
    """
    raises = partial(raises_test, cards.Hand)
    assert raises(doubled_down=6) == ValueError
    assert raises(doubled_down='spam') == ValueError
    assert raises(doubled_down=['spam', 'eggs']) == ValueError


def test_Hand_init_default():
    """Given parameters, :class:`blackjack.cards.Hand` should return
    a instance that uses given values for its attributes.
    """
    optionals = {
        'cards': (cards.Card(1, 0), cards.Card(2, 0)),
        '_iter_index': 1,
        'doubled_down': True,
    }
    hand = cards.Hand(**optionals)
    for attr in optionals:
        assert getattr(hand, attr) == optionals[attr]


# Tests for Hand_can_split.
def test_Hand_can_split(hand, hand_20):
    """When called, :meth:`Hand.can_split` should return whether the
    :class:`Hand` can be split.
    """
    assert hand_20.can_split()
    assert not hand.can_split()


# Tests for Hand_is_blackjack.
def test_Hand_is_blackjack(blackjack, hand_20, hand_21):
    """When called, :meth:`Hand.is_blackjack` should return whether the
    :class:`Hand` is a natural blackjack.
    """
    assert blackjack.is_blackjack()
    assert not hand_21.is_blackjack()
    assert not hand_20.is_blackjack()


# Tests for Hand.is_bust.
def test_Hand_is_bust(hand_20):
    """When called, :meth:`Hand.is_bust` should return whether the
    :class:`Hand` is bust.
    """
    assert not hand_20.is_bust()
    hand_20.append(cards.Card(10, 2))
    assert hand_20.is_bust()


# Tests for Hand.score.
def test_Hand_score(blackjack, hand, hand_20, hand_21):
    """When called, :meth:`Hand.score` should return the score of
    the :class:`Hand`.
    """
    assert blackjack.score() == [11, 21]
    assert hand.score() == [6, 16]
    assert hand_20.score() == [20,]
    assert hand_21.score() == [21,]


# Tests for Hand.serialize.
def test_Hand_serialize(hand):
    """When called, :meth:`Hand.serialize` should return the
    :class:`Hand` serialized as a JSON string.
    """
    assert hand.serialize() == json.dumps({
        'class': 'Hand',
        '_iter_index': 0,
        'cards': [
            '["Card", 1, "clubs", true]',
            '["Card", 2, "clubs", true]',
            '["Card", 3, "clubs", true]',
        ],
        'doubled_down': False,
    })


def test_Hand_split_valid(hand_20):
    """When called on a :class:`Hand` that can be split,
    :meth:`Hand.split` should split the :class:`Hand` and return
    the resulting two :class:`Hand` objects.
    """
    assert hand_20.split() == (
        cards.Hand([cards.Card(11, 0)]),
        cards.Hand([cards.Card(11, 1)]),
    )


def test_Hand_split_invalid(hand):
    """When called on a :class:`Hand` that cannot be split,
    :meth:`Hand.split` should raise a ValueError exception.
    """
    with pytest.raises(ValueError):
        _ = hand.split()
