"""
test_cards.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.cards module.
"""
import inspect
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
    
    def test_rank(self):
        """Card objects can be initialized with a suit value."""
        expected = 1
        
        c = cards.Card(expected)
        actual = c.rank
        
        self.assertEqual(expected, actual)
    
    def test_invalid_rank(self):
        """Card ranks must be between 1 and 13."""
        expected = ValueError
        with self.assertRaises(expected):
            _ = cards.Card(0)
    
    def test_suit(self):
        """Card objects can be initialized with a suit value."""
        expected = 'spades'
        
        c = cards.Card(10, expected)
        actual = c.suit
        
        self.assertEqual(expected, actual)
    
    def test_invalid_suit(self):
        """Card suits must be clubs, diamonds, hearts, or spades."""
        expected = ValueError
        with self.assertRaises(expected):
            _ = cards.Card(5, 'spam')
    
    def test_facing(self):
        """Card objects can be initiated with a facing value."""
        expected = True
        
        c = cards.Card(1, 1, cards.UP)
        actual = c.facing
        
        self.assertEqual(expected, actual)
    
    def test_invalid_facing(self):
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
    
    def test_equality_test(self):
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
    
    def test_equality_test_not_implemented(self):
        """Card objects should return not implemented when compared to 
        objects that aren't Card objets.
        """
        expected = NotImplemented
        
        c1 = cards.Card(2, 'hearts')
        other = 23
        actual = c1.__eq__(other)
        
        self.assertEqual(expected, actual)
    
    def test_nonequality_test(self):
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
    
    def test_cards(self):
        """An instance of Deck should be able to hold cards in its 
        cards attribute.
        """
        expected = [
            cards.Card(1, 3),
            cards.Card(2, 3),
            cards.Card(3, 3),
        ]
        
        d = cards.Deck(expected)
        actual = d.cards
        
        self.assertEqual(expected, actual)
    
    def test_build(self):
        """Deck.build() should return an instance of deck that 
        contains the cards needed for a blackjack game.
        """
        expected_size = 52
        expected_class = cards.Card
        
        d = cards.Deck.build()
        actual_size = len(d.cards)
        
        self.assertEqual(expected_size, actual_size)
        for card in d.cards:
            self.assertTrue(isinstance(card, expected_class))
    
    def test_build_casino_deck(self):
        """If given the number of standard decks to use, Deck.build() 
        should return a Deck object that contains cards from that many 
        standard decks.
        """
        num_decks = 6
        expected_size = 52 * num_decks
        expected_class = cards.Card
        
        d = cards.Deck.build(6)
        actual_size = len(d.cards)
        
        self.assertEqual(expected_size, actual_size)
        for card in d.cards:
            self.assertTrue(isinstance(card, expected_class))
    
    def test_sized_protocol(self):
        """Deck should implement the Sized protocol by returning the 
        number of cards in the deck for Deck.__len__."""
        expected = 52
        
        d = cards.Deck.build()
        actual = len(d)
        
        self.assertEqual(expected, actual)
    
    def test_equality_test(self):
        """Decks that contain the same cards in the same order should 
        be equal.
        """
        d1 = cards.Deck([
            cards.Card(1, 3),
            cards.Card(2, 3),
            cards.Card(3, 3),
        ])
        d2 = cards.Deck([
            cards.Card(1, 3),
            cards.Card(2, 3),
            cards.Card(3, 3),
        ])
        d3 = cards.Deck([
            cards.Card(1, 2),
            cards.Card(2, 3),
            cards.Card(3, 3),
        ])
        d4 = cards.Deck([
            cards.Card(1, 3),
            cards.Card(3, 3),
        ])
        d5 = cards.Deck([
            cards.Card(3, 3),
            cards.Card(1, 3),
            cards.Card(2, 3),
        ])
        
        self.assertTrue(d1 == d2)
        self.assertFalse(d1 == d3)
        self.assertFalse(d1 == d4)
        self.assertFalse(d1 == d5)
    
    def test_equality_notimplemented(self):
        """Attempts to compare a Deck object with a non-Deck object 
        should return NotImplemented.
        """
        expected = NotImplemented
        
        d1 = cards.Deck([
            cards.Card(1, 3),
            cards.Card(2, 3),
            cards.Card(3, 3),
        ])
        other = 'spam'
        actual = d1.__eq__(other)
        
        self.assertEqual(expected, actual)
    
    def test_copy(self):
        """Deck.copy() should return a copy of the Deck object."""
        


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
