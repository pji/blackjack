"""
test_players.py
~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.players module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from functools import partial
import inspect
import unittest

from blackjack import cards, players, game


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
    
    def test_chips(self):
        """If passed a number of chips, that number should be stored 
        in the chips attribute.
        """
        expected = 200
        
        p = players.Player(chips=expected)
        actual = p.chips
        
        self.assertEqual(expected, actual)
    
    def test_insured(self):
        """Player objects should initialize the insured attribute to 
        zero.
        """
        expected = 0
        player = players.Player()
        actual = player.insured
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
    
    def test_is_will_hit(self):
        """A will_hit function should accept a Player, a Hand, and a 
        Game objects.
        """
        player = players.Player()
        hand = cards.Hand([
            cards.Card(11, 0),
            cards.Card(11, 3),
        ])
        g = game.Game()
        _ = players.dealer_will_hit(player, hand, g)
        
    
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


class always_will_split(unittest.TestCase):
    def test_paramters(self):
        """Functions that follow the will_split protocol should 
        accept the following parameters: hand, player, dealer, 
        playerlist.
        """
        hand = cards.Hand()
        player = players.Player((hand,), 'John Cleese')
        g = game.Game()
        player.will_split = partial(players.always_will_split, None)
        player.will_split(hand, g)
        
        # The test was that no exception was raised when will_split 
        # was called.
        self.assertTrue(True)
    
    def test_always_true(self):
        """always_will_split() should return True."""
        hand = cards.Hand()
        player = players.Player((hand,), 'John Cleese')
        player.will_split = partial(players.always_will_split, None)
        actual = player.will_split(hand)
        
        self.assertTrue(actual)


class always_will_buyin(unittest.TestCase):
    def test_parameters(self):
        """Functions that follow the will_buyin protocol should 
        accept the following parameter: game.
        """
        player = players.Player()
        g = game.Game()
        
        player.will_buyin = partial(players.always_will_buyin, None)
        player.will_buyin(game)
        
        # The test was that no exception was raised when will_buyin 
        # was called.
        self.assertTrue(True)
    
    def test_always_true(self):
        """always_will_buyin() will always return True."""
        g = game.Game()
        p = players.Player()
        p.will_buyin = partial(players.always_will_buyin, None)
        actual = p.will_buyin(g)
        
        self.assertTrue(actual)


class will_double_down_alwaysTestCase(unittest.TestCase):
    def test_parameters(self):
        """Functions that follow the will_double_down protocol should 
        accept the following parameters: self, hand, game.
        """
        player = players.Player()
        hand = cards.Hand()
        g = game.Game()
        
        _ = players.will_double_down_always(player, hand, game)
        
        # The test was that no exception was raised when will_buyin 
        # was called.
        self.assertTrue(True)
    
    def test_always_true(self):
        """will_double_down_always() will always return True."""
        g = game.Game()
        h = cards.Hand()
        p = players.Player()
        actual = players.will_double_down_always(p, h, g)
        
        self.assertTrue(actual)


class will_insure_alwaysTestCase(unittest.TestCase):
    def test_parameters(self):
        """Functions that follow the will_insure protocol should 
        accept the following parameters: self, hand, game.
        """
        player = players.Player()
        hand = cards.Hand()
        g = game.Game()
        
        _ = players.will_insure_always(player, g)
        
        # The test was that no exception was raised when will_buyin 
        # was called.
        self.assertTrue(True)
    
    def test_always_max(self):
        """will_double_down_always() will always return the maximum 
        bet, which is half of the game's buy in."""
        expected = 10
        
        h = cards.Hand()
        p = players.Player()
        g = game.Game(None, None, (p,), None, 20)
        actual = players.will_insure_always(p, g)
        
        self.assertEqual(expected, actual)


class will_insure_neverTestCase(unittest.TestCase):
    def test_parameters(self):
        """Functions that follow the will_insure protocol should 
        accept the following parameters: self, game.
        """
        player = players.Player()
        hand = cards.Hand()
        g = game.Game()
        
        _ = players.will_insure_never(player, g)
        
        # The test was that no exception was raised when will_buyin 
        # was called.
        self.assertTrue(True)
    
    def test_always_zero(self):
        """will_double_down_always() will always return the maximum 
        bet, which is half of the game's buy in."""
        expected = 10
        
        h = cards.Hand()
        p = players.Player()
        g = game.Game(None, None, (p,), None, 20)
        actual = players.will_insure_always(p, g)
        
        self.assertEqual(expected, actual)


class playerfactoryTestCase(unittest.TestCase):
    def test_player_subclass(self):
        """playerfactory() should return Player subclasses."""
        expected = players.Player
        actual = players.playerfactory('Spam', None, None, None, None, None)
        self.assertTrue(issubclass(actual, expected))
    
    def test_will_hit(self):
        """Given a will_hit function, the subclass should have a 
        will_hit method.
        """
        expected = 'spam'
        
        def func(self, hand):
            return 'spam'
        Eggs = players.playerfactory('Eggs', func, None, None, None, None)
        obj = Eggs()
        actual = obj.will_hit(None)
        
        self.assertEqual(expected, actual)
    
    def test_will_split(self):
        """Given a will_split function, the subclass should have a 
        will_split method.
        """
        expected = False
        
        def func(self, hand, the_game):
            return False
        Spam = players.playerfactory('Spam', None, func, None, None, None)
        obj = Spam()
        actual = obj.will_split(None, None)
        
        self.assertEqual(expected, actual)
    
    def test_will_buyin(self):
        """Given a will_buyin function, the subclass should have a 
        will_buyin method.
        """
        expected = False
        
        def func(self, game):
            return False
        Spam = players.playerfactory('Spam', None, None, func, None, None)
        obj = Spam()
        actual = obj.will_buyin(None)
        
        self.assertEqual(expected, actual)
    
    def test_will_double_down(self):
        """Given a will_double_down function, the subclass should 
        have a will_double_down method.
        """
        expected = False
        
        def func(self, game):
            return False
        Spam = players.playerfactory('Spam', None, None, None, func, None)
        obj = Spam()
        actual = obj.will_double_down(None)
        
        self.assertEqual(expected, actual)
    
    def test_will_insure(self):
        """Given a will_insure function, the subclass should have a 
        will_insure method.
        """
        expected = 20
        
        def func(self, game):
            return 20
        Spam = players.playerfactory('Spam', None, None, None, None, func)
        obj = Spam()
        actual = obj.will_insure(None)
        
        self.assertEqual(expected, actual)
