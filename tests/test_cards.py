"""
test_cards.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.cards module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import collections.abc as col
from copy import deepcopy
import inspect
from itertools import zip_longest
import json
import unittest
from unittest.mock import call, Mock

from blackjack import cards


class CardTestCase(unittest.TestCase):
    def test_exists(self):
        """A class named Card should exist."""
        names = [item[0] for item in inspect.getmembers(cards)]
        self.assertTrue('Card' in names)
    
    def test_can_instantiate(self):
        """Card objects can be instantiated."""
        expected = cards.Card
        actual = cards.Card()
        self.assertTrue(isinstance(actual, expected))
    
    def test_deserialize(self):
        """When given a Card object serialized as a json string, 
        Card.deserialize() should return the deserialized Card object. 
        """
        exp = cards.Card(11, 0, True)
        s = '["Card", 11, "clubs", true]'
        act = cards.Card.deserialize(s)
        self.assertEqual(exp, act)
    
    def test___init__rank(self):
        """Card objects can be initialized with a suit value."""
        expected = 1
        
        c = cards.Card(expected)
        actual = c.rank
        
        self.assertEqual(expected, actual)
    
    def test___init__invalid_rank(self):
        """Card ranks must be between 1 and 13."""
        expected = ValueError
        with self.assertRaises(expected):
            _ = cards.Card(0)
    
    def test___init__suit(self):
        """Card objects can be initialized with a suit value."""
        expected = 'spades'
        
        c = cards.Card(10, expected)
        actual = c.suit
        
        self.assertEqual(expected, actual)
    
    def test___init__invalid_suit(self):
        """Card suits must be clubs, diamonds, hearts, or spades."""
        expected = ValueError
        with self.assertRaises(expected):
            _ = cards.Card(5, 'spam')
    
    def test___init__facing(self):
        """Card objects can be initiated with a facing value."""
        expected = True
        
        c = cards.Card(1, 1, cards.UP)
        actual = c.facing
        
        self.assertEqual(expected, actual)
    
    def test___init__invalid_facing(self):
        """Card facing must be a bool."""
        expected = ValueError
        with self.assertRaises(expected):
            c = cards.Card(1, 1, 'spam')
    
    def test___repr__(self):
        """Card should return a string useful for debugging."""
        expected = "Card(rank=10, suit='clubs', facing=True)"
        
        c = cards.Card(10, 'clubs', cards.UP)
        actual = c.__repr__()
        
        self.assertEqual(expected, actual)
    
    def test___str__(self):
        """Card objects should return a string suitable for printing."""
        expected = 'Q♥'
        
        c = cards.Card(12, 'hearts')
        actual = str(c)
        
        self.assertEqual(expected, actual)
    
    def test___str__print_should_hide_info_when_face_down(self):
        """When facing is down, __str__() should not reveal the suit 
        or rank of the card.
        """
        expected = '\u2500\u2500'
        
        c = cards.Card(11, 3, cards.DOWN)
        actual = c.__str__()
        
        self.assertEqual(expected, actual)
    
    def test___eq__equality_test(self):
        """Card objects should be compared for equality based on their 
        rank and suit.
        """
        c1 = cards.Card(2, 'hearts')
        c2 = cards.Card(2, 'hearts')
        c3 = cards.Card(11, 'clubs')
        c4 = cards.Card(2, 'spades')
        c5 = cards.Card(11, 'hearts')
        
        self.assertTrue(c1 == c2)
        self.assertFalse(c1 == c3)
        self.assertFalse(c1 == c4)
        self.assertFalse(c1 == c5)
    
    def test___eq__equality_test_not_implemented(self):
        """Card objects should return not implemented when compared to 
        objects that aren't Card objets.
        """
        expected = NotImplemented
        
        c1 = cards.Card(2, 'hearts')
        other = 23
        actual = c1.__eq__(other)
        
        self.assertEqual(expected, actual)
    
    def test___ne__nonequality_test(self):
        """Card objects should compare for non equality based on their 
        rank and suit.
        """
        c1 = cards.Card(2, 'hearts')
        c2 = cards.Card(2, 'hearts')
        c3 = cards.Card(11, 'clubs')
        c4 = cards.Card(2, 'spades')
        c5 = cards.Card(11, 'hearts')
        
        self.assertFalse(c1 != c2)
        self.assertTrue(c1 != c3)
        self.assertTrue(c1 != c4)
        self.assertTrue(c1 != c5)
    
    def test___lt__less_than(self):
        """If given another Card object, __lt__() should return True 
        if the Card object is less than the other Card object, and 
        False is the Card object is not.
        """
        c1 = cards.Card(11, 1)
        c2 = cards.Card(11, 1)
        c3 = cards.Card(10, 1)
        c4 = cards.Card(12, 1)
        c5 = cards.Card(11, 0)
        c6 = cards.Card(11, 2)
        c7 = cards.Card(10, 2)
        c8 = cards.Card(12, 0)
        
        self.assertFalse(c1 < c2)
        self.assertFalse(c1 < c3)
        self.assertTrue(c1 < c4)
        self.assertFalse(c1 < c5)
        self.assertTrue(c1 < c6)
        self.assertFalse(c1 < c7)
        self.assertTrue(c1 < c8)
    
    def test___lt__less_than_not_implemented(self):
        """If given a value that isn't a Card object, __lt__() should 
        return NotImplemented.
        """
        expected = NotImplemented
        
        c1 = cards.Card(11, 3)
        c2 = 'spam'
        actual = c1.__lt__(c2)
        
        self.assertEqual(expected, actual)
    
    def test__astuple(self):
        """When called, astuple() should return the card's attributes 
        as a tuple for serialization.
        """
        exp = ('Card', 11, 'clubs', True)
        card = cards.Card(*exp[1:])
        act = card._astuple()
        self.assertEqual(exp, act)
    
    def test__astuple_deserialize(self):
        """The result of astuple() should be able to be used to create 
        a new instance of cards.Card with the same attributes.
        """
        exp = cards.Card(11, 3, True)
        serialized = exp._astuple()
        act = cards.Card(*serialized[1:])
        self.assertEqual(exp, act)
    
    def test_flip_up(self):
        """When a Card object is face down, flip() should switch it to 
        being face up.
        """
        expected = cards.UP
        
        c = cards.Card(11, 0, cards.DOWN)
        c.flip()
        actual = c.facing
        
        self.assertEqual(expected, actual)
    
    def test_flip_down(self):
        """When a Card object is face up, flip() should switch it to 
        being face down.
        """
        expected = cards.DOWN
        
        c = cards.Card(11, 0, cards.UP)
        c.flip()
        actual = c.facing
        
        self.assertEqual(expected, actual)
    
    def test_serialize(self):
        """When called, serialize() returns a version of the object 
        serialized to a json string.
        """
        exp = '["Card", 11, "clubs", true]'
        card = cards.Card(11, 0, True)
        act = card.serialize()
        self.assertEqual(exp, act)


class PileTestCase(unittest.TestCase):
    # Utility methods.
    def cardlist(self):
        return [
            cards.Card(1, 0),
            cards.Card(2, 0),
            cards.Card(3, 0),
        ]
    
    # Tests.
    def test_exists(self):
        """A class named Pile should exist."""
        names = [item[0] for item in inspect.getmembers(cards)]
        self.assertTrue('Pile' in names)
    
    def test_can_instantiate(self):
        """An instance of Pile should be able to be instantiated."""
        expected = cards.Pile
        actual = cards.Pile()
        self.assertTrue(isinstance(actual, expected))
    
    def test_class_deserialize(self):
        """When given a Pile object serialized to a json string, 
        Pile.deserialize() should deserialize that object and 
        return it.
        """
        cardlist = [
            cards.Card(11, 0, True),
            cards.Card(12, 0, True),
            cards.Card(13, 0, True),
        ]
        exp = cards.Pile(cardlist)
        
        s = exp.serialize()
        act = cards.Pile.deserialize(s)
        
        self.assertEqual(exp, act)
   
    def test_cards(self):
        """An instance of Pile should be able to hold cards in its 
        cards attribute.
        """
        expected = (
            cards.Card(1, 3),
            cards.Card(2, 3),
            cards.Card(3, 3),
        )
        
        d = cards.Pile(expected)
        actual = d.cards
        
        self.assertEqual(expected, actual)
    
    def test__iter_index(self):
        """An instance of Pile should initialize the iter_index 
        attribute to zero.
        """
        expected = 0
        
        d = cards.Pile()
        actual = d._iter_index
        
        self.assertEqual(expected, actual)
    
    def test_sized_protocol(self):
        """Pile should implement the Sized protocol by returning the 
        number of cards in the deck for Pile.__len__."""
        expected = 3
        
        d = cards.Pile(self.cardlist())
        actual = len(d)
        
        self.assertEqual(expected, actual)
    
    def test_equality_test(self):
        """Piles that contain the same cards in the same order should 
        be equal.
        """
        d1 = cards.Pile([
            cards.Card(1, 3),
            cards.Card(2, 3),
            cards.Card(3, 3),
        ])
        d2 = cards.Pile([
            cards.Card(1, 3),
            cards.Card(2, 3),
            cards.Card(3, 3),
        ])
        d3 = cards.Pile([
            cards.Card(1, 2),
            cards.Card(2, 3),
            cards.Card(3, 3),
        ])
        d4 = cards.Pile([
            cards.Card(1, 3),
            cards.Card(3, 3),
        ])
        d5 = cards.Pile([
            cards.Card(3, 3),
            cards.Card(1, 3),
            cards.Card(2, 3),
        ])
        
        self.assertTrue(d1 == d2)
        self.assertFalse(d1 == d3)
        self.assertFalse(d1 == d4)
        self.assertFalse(d1 == d5)
    
    def test_equality_notimplemented(self):
        """Attempts to compare a Pile object with a non-Pile object 
        should return NotImplemented.
        """
        expected = NotImplemented
        
        d1 = cards.Pile([
            cards.Card(1, 3),
            cards.Card(2, 3),
            cards.Card(3, 3),
        ])
        other = 'spam'
        actual = d1.__eq__(other)
        
        self.assertEqual(expected, actual)
    
    def test_copy(self):
        """Pile.copy() should return a shallow copy of the Pile 
        object.
        """
        expected = cards.Pile([
            cards.Card(1, 3),
            cards.Card(2, 3),
            cards.Card(3, 3),
        ])
        
        actual = expected.copy()
        
        self.assertEqual(expected, actual)
        self.assertFalse(expected is actual)
        for i in range(len(actual)):
            self.assertTrue(expected.cards[i] is actual.cards[i])
    
    def test_iterator_protocol(self):
        """Pile implements the iterator protocol."""
        expected = col.Iterator
        d = cards.Pile()
        self.assertTrue(isinstance(d, expected))
    
    def test___next___increment(self):
        """Calls to __next__() should increment the Pile object's 
        _iter_index attribute.
        """
        expected = 2
        
        d = cards.Pile(self.cardlist())
        next(d)
        next(d)
        actual = d._iter_index
        
        self.assertEqual(expected, actual)
    
    def test___next___stop(self):
        """If _iter_index is equal to or greater than the number of 
        cards in the Pile object, __next__() should raise 
        StopIteration.
        """
        expected = StopIteration
        
        d = cards.Pile(self.cardlist())
        d._iter_index = 3
        
        with self.assertRaises(expected):
            _ = next(d)
            
    def test___next___return(self):
        """__next__() should return the next card held by the Pile 
        object.
        """
        card_list = [
            cards.Card(1, 0),
            cards.Card(2, 0),
        ]
        expected = card_list[1]
        
        d = cards.Pile(card_list)
        d._iter_index = 1
        actual = next(d)
        
        self.assertEqual(expected, actual)
    
    def test___iter__(self):
        """__iter__() should return a copy of of the Pile object for 
        iteration.
        """
        card_list = [
            cards.Card(1, 0),
            cards.Card(2, 0),
        ]
        expected = cards.Pile(card_list)
        
        actual = expected.__iter__()
        
        self.assertEqual(expected, actual)
        self.assertFalse(expected is actual)
    
    def test_card_iteratation(self):
        """The cards in Pile.card should be able to be iterated."""
        expected = 3
        
        d = cards.Pile(self.cardlist())
        actual = 0
        for card in d:
            actual += 1
        
        self.assertEqual(expected, actual)
    
    def test_container_protocol(self):
        """Pile should implement the Container protocol."""
        expected = col.Container
        d = cards.Pile()
        self.assertTrue(isinstance(d, col.Container))
    
    def test___contains__(self):
        """Pile should implement the in operator."""
        c1 = cards.Card(1, 0)
        c2 = cards.Card(2, 0)
        c3 = cards.Card(3, 0)
        d = cards.Pile([c1, c2])
        self.assertTrue(c1 in d)
        self.assertFalse(c3 in d)
    
    def test_reversible_protocol(self):
        """Pile should implement the Reversible protocol."""
        expected = col.Reversible
        d = cards.Pile()
        self.assertTrue(isinstance(d, expected))
    
    def test___reversed__(self):
        """__reversed__ should return an iterator that iterates 
        though the cards in the Pile object in reverse order.
        """
        card_list = [
            cards.Card(1, 0),
            cards.Card(2, 0),
            cards.Card(3, 0),
        ]
        expected = cards.Pile(card_list[::-1])
        
        d = cards.Pile(card_list)
        actual = d.__reversed__()
        
        self.assertEqual(expected, actual)
    
    def test_sequence_protocol(self):
        """Pile should implement the Sequence protocol."""
        expected = col.Sequence
        d = cards.Pile()
        self.assertTrue(isinstance(d, expected))
    
    def test___getitem__(self):
        """Given a key, __getitem__ should return the item for that 
        key.
        """
        card_list = [
            cards.Card(1, 0),
            cards.Card(2, 0),
            cards.Card(3, 0),
        ]
        expected = card_list[1]
        
        d = cards.Pile(card_list)
        actual = d.__getitem__(1)
        
        self.assertEqual(expected, actual)
    
    def test_mutablesequence_protocol(self):
        """Pile should implement the MutableSequence protocol."""
        expected = col.MutableSequence
        d = cards.Pile()
        self.assertTrue(isinstance(d, expected))
    
    def test___setitem__(self):
        """Given a key and value, __setitem__ should set the value of 
        cards at that index to the value.
        """
        expected = cards.Card(11, 3)
        
        d = cards.Pile(self.cardlist())
        d.__setitem__(1, expected)
        actual = d.cards[1]
        
        self.assertEqual(expected, actual)
    
    def test___delitem__(self):
        """Given a key, __delitem__ should delete the item at that key 
        of cards.
        """
        card_list = [
            cards.Card(1, 0),
            cards.Card(2, 0),
            cards.Card(3, 0),
        ]
        expected = (card_list[0], card_list[2])
        
        d = cards.Pile(card_list)
        d.__delitem__(1)
        actual = d.cards
        
        self.assertEqual(expected, actual)
    
    def test_insert(self):
        """Given a key and an object, insert() should insert the item
        at the key.
        """
        expected = cards.Card(11, 3)

        d = cards.Pile(self.cardlist())
        d.insert(1, expected)
        actual = d.cards[1]

        self.assertEqual(expected, actual)
    
    def test_serialize(self):
        """When called, serialize() should return the Pile object 
        serialized to a JSON string.
        """
        exp = json.dumps({
            'class': 'Pile',
            '_iter_index': 0,
            'cards': [
                '["Card", 11, "clubs", true]',
                '["Card", 12, "clubs", true]',
                '["Card", 13, "clubs", true]',
            ]
        })
        
        cardlist = [
            cards.Card(11, 0, True),
            cards.Card(12, 0, True),
            cards.Card(13, 0, True),
        ]
        pile = cards.Pile(cardlist)
        act = pile.serialize()
        
        self.assertEqual(exp, act)


class DeckTestCase(unittest.TestCase):
    def test_exists(self):
        """A class named Deck should exist."""
        names = [item[0] for item in inspect.getmembers(cards)]
        self.assertTrue('Deck' in names)
    
    def test_can_instantiate(self):
        """An instance of Deck should be able to be instantiated."""
        expected = cards.Deck
        actual = cards.Deck()
        self.assertTrue(isinstance(actual, expected))
    
    def test_Pile_subclass(self):
        """Deck should be a subclass of Pile."""
        expected = cards.Pile
        actual = cards.Deck
        self.assertTrue(issubclass(actual, expected))
    
    def test_build(self):
        """Pile.build() should return an instance of deck that 
        contains the cards needed for a blackjack game.
        """
        expected_len = 52
        expected_size = 1
        expected_class = cards.Card
        
        
        d = cards.Deck.build()
        actual_len = len(d.cards)
        actual_size = d.size
        
        self.assertEqual(expected_len, actual_len)
        self.assertEqual(expected_size, actual_size)
        for card in d.cards:
            self.assertTrue(isinstance(card, expected_class))
    
    def test_deserialize(self):
        """When given a Deck serialized as a JSON string, deserialize() 
        should return the deserialized Deck object.
        """
        cardlist = [
            cards.Card(11, 0, True),
            cards.Card(12, 0, True),
            cards.Card(13, 0, True),
        ]
        exp = cards.Pile(cardlist)
        
        s = exp.serialize()
        act = cards.Pile.deserialize(s)
        
        self.assertEqual(exp, act)
    
    def test_build_cards_face_down(self):
        """Card objects should be face down in the deck."""
        expected = cards.DOWN
        
        d = cards.Deck.build()
        for c in d:
            actual = c.facing
            
            self.assertEqual(expected, actual)
    
    def test_build_casino_deck(self):
        """If given the number of standard decks to use, Pile.build() 
        should return a Pile object that contains cards from that many 
        standard decks.
        """
        expected_size = 6
        expected_len = 52 * expected_size
        expected_class = cards.Card
        
        d = cards.Deck.build(expected_size)
        actual_len = len(d.cards)
        actual_size = d.size
        
        self.assertEqual(expected_len, actual_len)
        self.assertEqual(expected_size, actual_size)
        for card in d.cards:
            self.assertTrue(isinstance(card, expected_class))
    
    def test_build_each_card_unique(self):
        """When build() uses multiple decks, each card should still 
        be a unique object.
        """
        deck = cards.Deck.build(2)
        for i in range(52):
            self.assertFalse(deck[i] is deck[i + 52])
    
    def test_draw_a_card(self):
        """draw() should remove the "top card" of the deck and return 
        it. For performance reasons, "top card" is defined as the 
        card at index -1.
        """
        card_list = [
            cards.Card(1, 0),
            cards.Card(2, 0),
            cards.Card(3, 0),
        ]
        expected_card = card_list[-1]
        expected_deck = cards.Pile(card_list[0:2])
        
        d = cards.Deck(card_list)
        actual_card = d.draw()
        actual_deck = d
        
        self.assertEqual(expected_card, actual_card)
        self.assertEqual(expected_deck, actual_deck)
    
    def test_shuffle(self):
        """shuffle() should randomize the order of the deck.
        
        NOTE: Because shuffling is a random action, it's possible 
        for this to fail because the randomized order ends up the 
        same as the original order. The odds for this should be 
        1 in 52!, which is around 8 * 10^67.
        """
        original = cards.Deck.build()
        expected_len = len(original)
        
        d = deepcopy(original)
        d.shuffle()
        actual_len = len(d)
        
        self.assertNotEqual(original, d)
        self.assertEqual(expected_len, actual_len)
    
    def test_random_cut_end_of_deck(self):
        """In order to make counting cards more difficult, cut() 
        should remove a random amount, between 60 and 75, cards from 
        the deck.
        
        NOTE: Since the number of cards removed is random, this test 
        will run 10 times to try to catch issues with the number 
        generation.
        """
        num_decks = 6
        original_len = 52 * num_decks
        too_few_cards = original_len - 76
        too_many_cards = original_len - 59
        lengths = []
        
        for i in range(10): 
            d = cards.Deck.build(num_decks)
            d.random_cut()
            actual_len = len(d)
            lengths.append(actual_len)
            
            self.assertNotEqual(original_len, actual_len)
            self.assertTrue(actual_len > too_few_cards)
            self.assertTrue(actual_len < too_many_cards)
        
        length = lengths.pop()
        comp_lengths = [length == n for n in lengths]
        self.assertFalse(all(comp_lengths))
    
    def test_serialize(self):
        """When called, serialize() should return the Deck object 
        serialized as a JSON string.
        """
        exp = json.dumps({
            'class': 'Deck',
            '_iter_index': 0,
            'cards': [
                '["Card", 11, "clubs", true]',
                '["Card", 12, "clubs", true]',
                '["Card", 13, "clubs", true]',
            ],
            'size': 1
        })
        
        cardlist = [
            cards.Card(11, 0, True),
            cards.Card(12, 0, True),
            cards.Card(13, 0, True),
        ]
        deck = cards.Deck(cardlist)
        act = deck.serialize()
        
        self.assertEqual(exp, act)


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
