"""
test_players.py
~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.players module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import inspect
import unittest

from blackjack import cards, players


class PlayerTestCase(unittest.TestCase):
    def test_exists(self):
        """A class named Player should exist."""
        names = [item[0] for item in inspect.getmembers(players)]
        self.assertTrue('Player' in names)
    
    def test_can_be_subclassed(self):
        """Player should be able to be subclassed."""
        expected = players.Player
        
        class Spam(players.Player):
            pass
        actual = Spam
        
        self.assertTrue(issubclass(actual, expected))
    
    def test_hands_initiated_with_no_Hand(self):
        """The hands attribute should be an empty tuple if a Hand 
        object is not passed during initialization.
        """
        expected = ()
        
        class Spam(players.Player):
            pass
        obj = Spam()
        actual = obj.hands
        
        self.assertEqual(expected, actual)
    
    def test_name(self):
        """If passed a name, the name attribute should be initialized 
        with that name.
        """
        expected = 'Spam'
        
        p = players.Player(name=expected)
        actual = p.name
        
        self.assertEqual(expected, actual)
    
    def test___str__(self):
        """__str__() should return the name of the Player object."""
        expected = 'Spam'
        
        p = players.Player(name=expected)
        actual = p.__str__()
        
        self.assertEqual(expected, actual)
    
    def test___format__(self):
        """__format__() should return as though it was called on the 
        value of the name attribute.
        """
        tmp = '{:<6}'
        expected = tmp.format('spam')
        
        p = players.Player(name='spam')
        actual = tmp.format(p)
        
        self.assertEqual(expected, actual)


class dealer_will_hitTestCase(unittest.TestCase):
    def test_exists(self):
        """A function named dealer_will_hit() should exist."""
        names = [item[0] for item in inspect.getmembers(players)]
        self.assertTrue('dealer_will_hit' in names)
    
    def test_stand_on_bust(self):
        """If the hand is bust, dealer_will_hit() should return 
        False.
        """
        expected = players.STAND
        
        h = cards.Hand([
            cards.Card(11, 0),
            cards.Card(4, 2),
            cards.Card(11, 3),
        ])
        actual = players.dealer_will_hit(None, h)
        
        self.assertEqual(expected, actual)
    
    def test_stand_on_17_plus(self):
        """If the score of the hand is 17 or greater, dealer_will_hit() 
        should return False.
        """
        expected = players.STAND
        
        h1 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(7, 2),
        ])
        h2 = cards.Hand([
            cards.Card(12, 1),
            cards.Card(2, 3),
            cards.Card(8, 1),
        ])
        actual_h1 = players.dealer_will_hit(None, h1)
        actual_h2 = players.dealer_will_hit(None, h2)
        
        self.assertEqual(expected, actual_h1)
        self.assertEqual(expected, actual_h2)
    
    def test_hit_on_less_than_17(self):
        """If the score of the hand is less than 17, dealer_will_hit() 
        should return true.
        """
        expected = players.HIT
        
        h1 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(6, 2),
        ])
        h2 = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3),
            cards.Card(8, 1),
        ])
        actual_h1 = players.dealer_will_hit(None, h1)
        actual_h2 = players.dealer_will_hit(None, h2)
        
        self.assertEqual(expected, actual_h1)


class playerfactoryTestCase(unittest.TestCase):
    def test_player_subclass(self):
        """playerfactory() should return Player subclasses."""
        expected = players.Player
        actual = players.playerfactory('Spam', None)
        self.assertTrue(issubclass(actual, expected))
    
    def test_will_hit(self):
        """Given a will_hit function, the subclass should have a 
        will_hit method.
        """
        expected = 'spam'
        
        def test_method(self, hand):
            return 'spam'
        Eggs = players.playerfactory('Eggs', test_method)
        obj = Eggs()
        actual = obj.will_hit(None)
        
        self.assertEqual(expected, actual)