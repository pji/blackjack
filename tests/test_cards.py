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
