"""
test_cards.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.cards module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import collections.abc as col
import inspect
import json
import unittest
from copy import deepcopy
from itertools import chain, zip_longest
from random import seed
from unittest.mock import call, Mock

import pytest

from blackjack import cards


# Tests for Card.
@pytest.fixture
def testcard():
    """An instance of :class:`blackjack.cards.Card` for testing."""
    yield cards.Card(10, 'clubs', cards.UP)


# Tests for Card class methods.
def test_deserialize(testcard):
    """When given a :class:`blackjack.cards.Card` object serialized as
    a json string, :meth:`blackjack.cards.Card.deserialize()`` should
    return the deserialized object.
    """
    s = '["Card", 10, "clubs", true]'
    assert cards.Card.deserialize(s) == testcard


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
    optionals = {
        'rank': 23,
        'suit': 'spam',
        'facing': 'spam',
    }
    for attr in optionals:
        kwarg = {attr: optionals[attr]}
        with pytest.raises(ValueError):
            card = cards.Card(**kwarg)


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
def test_Card___repr__(testcard):
    """:class:`blackjack.cards.Card.__repr__` should return a string
    useful for debugging.
    """
    assert repr(testcard) == "Card(rank=10, suit='clubs', facing=True)"


def test_Card___str__(testcard):
    """:class:`blackjack.cards.Card.__str__` should return a string
    useful for printing.
    """
    assert str(testcard) == '10♣︎'


def test_Card___str__(testcard):
    """:class:`blackjack.cards.Card.__str__` should return a string
    useful for printing. If the card is face down, the suit and rank
    information should be hidden.
    """
    testcard.facing = cards.DOWN
    assert str(testcard) == '\u2500\u2500'


def test_Card_comparisons(testcard):
    """:class:`blackjack.cards.Card` objects should be compared for
    equality based on their rank and suit.
    """
    assert testcard == cards.Card(10, 'clubs', cards.UP)
    assert testcard == cards.Card(10, 'clubs', cards.DOWN)
    assert testcard != cards.Card(11, 'clubs')
    assert testcard != cards.Card(10, 'hearts')
    assert testcard != cards.Card(9, 'diamonds')
    assert testcard < cards.Card(11, 'clubs')
    assert testcard <= cards.Card(12, 'clubs')
    assert testcard < cards.Card(10, 'diamonds')
    assert testcard <= cards.Card(10, 'diamonds')
    assert testcard > cards.Card(9, 'clubs')
    assert testcard >= cards.Card(9, 'clubs')
    assert cards.Card(10, 'diamonds') > testcard
    assert cards.Card(10, 'diamonds') >= testcard
    assert testcard.__eq__(23) == NotImplemented


# Tests for Card._astuple.
def test_Card__astuple(testcard):
    """When called, :meth:`blackjack.cards.Card._astuple` should return
    the card's attributes as a tuple for serialization.
    """
    assert testcard._astuple() == ('Card', 10, 'clubs', True)


# Tests for Card.flip.
def test_Card_flip_up(testcard):
    """When a :class:`blackjack.cards.Card` object is face down,
    :meth:`blackjack.cards.Card.flip` should switch it to
    being face up. If the object is face down, it should switch
    it to face up.
    """
    testcard.flip()
    assert testcard.facing == cards.DOWN
    testcard.flip()
    assert testcard.facing == cards.UP


# Tests for Card.serialize.
def test_Card_serialize(testcard):
    """When called, :meth:`blackjack.cards.Card.serialize` returns a
    version of the object serialized to a json string.
    """
    assert testcard.serialize() == '["Card", 10, "clubs", true]'


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


class HandTestCase(unittest.TestCase):
    # Utility methods.
    def cardlist(self):
        return (
            cards.Card(1, 0),
            cards.Card(2, 0),
            cards.Card(3, 0),
        )

    # Tests.
    def test_Pile_subclass(self):
        """Hand should be a subclass of Pile."""
        expected = cards.Pile
        actual = cards.Hand
        self.assertTrue(issubclass(actual, expected))

    def test_can_instantiate(self):
        """An instance of Hand should be able to be instantiated."""
        expected = cards.Hand
        actual = cards.Hand()
        self.assertTrue(isinstance(actual, expected))

    def test_append(self):
        """Given a Card object, append() should append that card to
        cards.
        """
        expected = self.cardlist()

        h = cards.Hand(expected[:2])
        h.append(expected[2])
        actual = h.cards

        self.assertEqual(expected, actual)

    def test_can_split_true(self):
        """can_split() should return true if the hand can be split."""
        cardlist = [
            cards.Card(10, 0),
            cards.Card(10, 2),
        ]
        h = cards.Hand(cardlist)
        actual = h.can_split()

        self.assertTrue(actual)

    def test_can_split_false(self):
        """can_split() should return false if the hand cannot be
        split.
        """
        cardlist = [
            cards.Card(10, 0),
            cards.Card(11, 2),
        ]
        h = cards.Hand(cardlist)
        actual = h.can_split()

        self.assertFalse(actual)

    def test_deserialize(self):
        """When given a Hand object serialized as a JSON string,
        deserialize() should return the deserialized object.
        """
        cardlist = [
            cards.Card(11, 0, True),
            cards.Card(12, 0, True),
            cards.Card(13, 0, True),
        ]
        exp = cards.Hand(cardlist)

        s = exp.serialize()
        act = cards.Hand.deserialize(s)

        self.assertEqual(exp, act)

    def test_doubled_down_initialized(self):
        """Hand objects should have a doubled_down attribute that
        is initialized to False.
        """
        hand = cards.Hand()
        self.assertFalse(hand.doubled_down)

    def test_is_blackjack_true(self):
        """is_blackjack() should return true if the hand is a natural
        blackjack.
        """
        cardlist = [
            cards.Card(11, 3),
            cards.Card(1, 2),
        ]
        h = cards.Hand(cardlist)
        actual = h.is_blackjack()

        self.assertTrue(actual)

    def test_is_blackjack_false_two_cards(self):
        """is_blackjack() should return false if the hand doesn't
        equal 21.
        """
        cardlist = [
            cards.Card(11, 3),
            cards.Card(4, 2),
        ]
        h = cards.Hand(cardlist)
        actual = h.is_blackjack()

        self.assertFalse(actual)

    def test_is_blackjack_false_three_cards(self):
        """is_blackjack() should return false if the hand has more
        than two cards.
        """
        cardlist = [
            cards.Card(11, 3),
            cards.Card(4, 2),
            cards.Card(7, 3),
        ]
        h = cards.Hand(cardlist)
        actual = h.is_blackjack()

        self.assertFalse(actual)

    def test_is_bust(self):
        """When called, is_bust() should return true if the score of
        the hand is over 21.
        """
        exp = True

        hand = cards.Hand((
            cards.Card(11, 0),
            cards.Card(11, 0),
            cards.Card(11, 0),
        ))
        act = hand.is_bust()

        self.assertEqual(exp, act)

    def test_is_bust_false(self):
        """When called, is_bust() should return true if their are
        possible scores under 21.
        """
        exp = False

        hand = cards.Hand((
            cards.Card(1, 0),
            cards.Card(1, 0),
            cards.Card(1, 0),
        ))
        act = hand.is_bust()

        self.assertEqual(exp, act)

    def test_score(self):
        """score() should add together the values of the cards in the
        hand and return the score.
        """
        expected = [18,]

        cardlist = [
            cards.Card(11, 3),
            cards.Card(8, 2),
        ]
        h = cards.Hand(cardlist)
        actual = h.score()

        self.assertEqual(expected, actual)

    def test_score_ace(self):
        """score() should return all unique scores if there is an
        ace in the hand.
        """
        expected = [
            4,      # 1, 1, 2
            14,     # 1, 11, 2 & 11, 1, 2
            24,     # 11, 11, 2
        ]

        cardlist = [
            cards.Card(1, 0),
            cards.Card(1, 1),
            cards.Card(2, 3),
        ]
        h = cards.Hand(cardlist)
        actual = h.score()

        self.assertEqual(expected, actual)

    def test_serialize(self):
        """When called, serialize() should return the object
        serialized as a JSON string.
        """
        exp = json.dumps({
            'class': 'Hand',
            '_iter_index': 0,
            'cards': [
                '["Card", 11, "clubs", true]',
                '["Card", 12, "clubs", true]',
                '["Card", 13, "clubs", true]',
            ],
            'doubled_down': False,
        })

        cardlist = [
            cards.Card(11, 0, True),
            cards.Card(12, 0, True),
            cards.Card(13, 0, True),
        ]
        hand = cards.Hand(cardlist)
        act = hand.serialize()

        self.assertEqual(exp, act)

    def test_split_valid(self):
        """If the hand can be split, split() should return two Hand
        objects, each containing one of the cards of the split hand.
        """
        cardlist = [
            cards.Card(11, 0),
            cards.Card(11, 3),
        ]
        expected = (
            cards.Hand([cardlist[0],]),
            cards.Hand([cardlist[1],]),
        )

        h = cards.Hand(cardlist)
        actual = h.split()

        self.assertEqual(expected, actual)

    def test_split_invalid(self):
        """If the hand cannot be split, split() should raise a
        ValueError exception.
        """
        expected = ValueError

        h = cards.Hand([
            cards.Card(11, 0),
            cards.Card(2, 3),
        ])

        with self.assertRaises(ValueError):
            _ = h.split()


class validate_cardtuple(unittest.TestCase):
    def test_valid(self):
        """Given a valid value, validate_cardtuple should normalize
        and validate it then return the normalized value.
        """
        exp = (
            cards.Card(11, 3),
            cards.Card(1, 1),
        )

        value = list(exp)
        act = cards.validate_cardtuple(None, value)

        self.assertEqual(exp, act)


class validate_deckTestCase(unittest.TestCase):
    def test_valid(self):
        """Given a valid value, validate_deck should validate and
        return it.
        """
        exp = cards.Deck.build(3)
        act = cards.validate_deck(None, exp)
        self.assertEqual(exp, act)

    def test_invalid(self):
        """Given an invalid value, validate_deck should raise a
        ValueError exception.
        """
        exp = ValueError

        class Spam:
            msg = '{}'
        value = 'eggs'

        with self.assertRaises(exp):
            _ = cards.validate_deck(Spam(), value)


class validate_handtuple(unittest.TestCase):
    def test_valid(self):
        """Given a valid value, validate_handtuple should normalize
        and validate it then return the normalized value.
        """
        exp = (
            cards.Hand((
                cards.Card(11, 3),
                cards.Card(1, 1),
            )),
            cards.Hand((
                cards.Card(3, 1),
                cards.Card(5, 1),
            )),
        )

        value = list(exp)
        act = cards.validate_handtuple(None, value)

        self.assertEqual(exp, act)


class validate_rankTestCase(unittest.TestCase):
    def test_exists(self):
        """A function named validate_rank should exist."""
        names = [item[0] for item in inspect.getmembers(cards)]
        self.assertTrue('validate_rank' in names)

    def test_valid(self):
        """validate_rank should accept ints from 1 to 13."""
        expected = 9
        actual = cards.validate_rank(None, expected)
        self.assertEqual(expected, actual)

    def test_invalid_type(self):
        """validate_rank should reject data that cannot be coerced
        into an int by raising a TypeError.
        """
        expected = TypeError

        class Spam:
            msg = '{}'

        with self.assertRaises(expected):
            _ = cards.validate_rank(Spam(), 'spam')

    def test_invalid_too_low(self):
        """validate_rank should reject values less than 1 by raising
        a ValueError."""
        expected = ValueError

        class Spam:
            msg = '{}'

        with self.assertRaises(expected):
            _ = cards.validate_rank(Spam(), -3)

    def test_invalid_too_high(self):
        """vaidate_rank should reject values more than 13 by raising
        a ValueError.
        """
        expected = ValueError

        class Spam:
            msg = '{}'

        with self.assertRaises(expected):
            _ = cards.validate_rank(Spam(), 14)


class validate_suitTestCase(unittest.TestCase):
    def test_exist(self):
        """A function named validate_suit shold exist."""
        names = [item[0] for item in inspect.getmembers(cards)]
        self.assertTrue('validate_suit' in names)

    def test_valid(self):
        """validate_suit should accept the names of the four suits
        as strings.
        """
        expected = 'hearts'
        actual = cards.validate_suit(None, expected)
        self.assertEqual(expected, actual)

    def test_invalid(self):
        """validate_suit should reject invalid values not in the list
        of valid suits by raising a ValueError.
        """
        expected = ValueError

        class Spam:
            msg = '{}'

        with self.assertRaises(expected):
            _ = cards.validate_suit(Spam(), 'eggs')

    def test_normalize_index(self):
        """If passed the index of a valid suit in the suit list,
        validate_suit should normalize the value to the name of that
        suit.
        """
        expected = 'clubs'

        class Spam:
            msg = '{}'

        actual = cards.validate_suit(Spam(), 0)
        self.assertEqual(expected, actual)

    def test_normalize_case(self):
        """validate_suit should normalize passed strings to lowercase
        before comparing them to the list of valid values.
        """
        expected = 'diamonds'

        class Spam:
            msg = '{}'

        actual = cards.validate_suit(Spam(), 'Diamonds')
        self.assertEqual(expected, actual)
