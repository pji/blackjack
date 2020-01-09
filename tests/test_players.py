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
from unittest.mock import patch

from blackjack import cards, players, game, model


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


class will_hit_dealerTestCase(unittest.TestCase):
    def test_exists(self):
        """A function named will_hit_dealer() should exist."""
        names = [item[0] for item in inspect.getmembers(players)]
        self.assertTrue('will_hit_dealer' in names)
    
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
        _ = players.will_hit_dealer(player, hand, g)
    
    def test_stand_on_bust(self):
        """If the hand is bust, will_hit_dealer() should return 
        False.
        """
        expected = players.STAND
        
        h = cards.Hand([
            cards.Card(11, 0),
            cards.Card(4, 2),
            cards.Card(11, 3),
        ])
        actual = players.will_hit_dealer(None, h)
        
        self.assertEqual(expected, actual)
    
    def test_stand_on_17_plus(self):
        """If the score of the hand is 17 or greater, will_hit_dealer() 
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
        actual_h1 = players.will_hit_dealer(None, h1)
        actual_h2 = players.will_hit_dealer(None, h2)
        
        self.assertEqual(expected, actual_h1)
        self.assertEqual(expected, actual_h2)
    
    def test_hit_on_less_than_17(self):
        """If the score of the hand is less than 17, will_hit_dealer() 
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
        actual_h1 = players.will_hit_dealer(None, h1)
        actual_h2 = players.will_hit_dealer(None, h2)
        
        self.assertEqual(expected, actual_h1)


class will_hit_recommendedTestCase(unittest.TestCase):
    def test_dealer_card_good_hit_if_not_17(self):
        """If the dealer's up card is 7-11, the player should hit 
        until their hand's total is 17 or greater.
        """
        expected = True
        
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(6, 2),
        ])
        player = players.Player(phand, 'John')
        dhand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, 20)
        actual = players.will_hit_recommended(None, phand, g)
        
        self.assertEqual(expected, actual)
    
    def test_dealer_card_fair_hit_if_not_13(self):
        """If the dealer's up card is 2-3, the player should hit 
        until their hand's total is 17 or greater.
        """
        expected = True
        
        phand = cards.Hand([
            cards.Card(5, 1),
            cards.Card(7, 2),
        ])
        player = players.Player(phand, 'John')
        dhand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, 20)
        actual = players.will_hit_recommended(None, phand, g)
        
        self.assertEqual(expected, actual)
    
    def test_dealer_card_poor_hit_if_not_12(self):
        """If the dealer's up card is 2-3, the player should hit 
        until their hand's total is 17 or greater.
        """
        expected = True
        
        phand = cards.Hand([
            cards.Card(4, 1),
            cards.Card(7, 2),
        ])
        player = players.Player(phand, 'John')
        dhand = cards.Hand([
            cards.Card(5, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, 20)
        actual = players.will_hit_recommended(None, phand, g)
        
        self.assertEqual(expected, actual)
    
    def test_hit_soft_if_not_18(self):
        """If the player's hand contains an ace and is less than 19, 
        the player should hit.
        """
        expected = True
        
        phand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(7, 2),
        ])
        player = players.Player(phand, 'John')
        dhand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, 20)
        actual = players.will_hit_recommended(None, phand, g)
        
        self.assertEqual(expected, actual)
    
    def test_do_not_hit_soft_19(self):
        """If the player's hand is a soft 19, don't hit."""
        expected = False
        
        phand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(6, 2),
            cards.Card(2, 2),
        ])
        player = players.Player(phand, 'John')
        dhand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, 20)
        actual = players.will_hit_recommended(None, phand, g)
        
        self.assertEqual(expected, actual)
    
    def test_stand(self):
        """If the situation doesn't match the above criteria, stand."""
        expected = False
        
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(11, 2),
        ])
        player = players.Player(phand, 'John')
        dhand = cards.Hand([
            cards.Card(5, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, 20)
        actual = players.will_hit_recommended(None, phand, g)
        
        self.assertEqual(expected, actual)
    
    def test_stand_bust(self):
        """If the hand is bust, stand."""
        expected = False
        
        phand = cards.Hand([
            cards.Card(8, 2),
            cards.Card(6, 1),
            cards.Card(2, 1),
            cards.Card(7, 2),
        ])
        player = players.Player(phand, 'John')
        dhand = cards.Hand([
            cards.Card(5, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, 20)
        actual = players.will_hit_recommended(None, phand, g)
        
        self.assertEqual(expected, actual)


class will_hit_userTestCase(unittest.TestCase):
    @patch('blackjack.game.BaseUI.input')
    def test_hit(self, mock_input):
        """When the user chooses to hit, will_hit_user() returns 
        True.
        """
        expected = True
        
        mock_input.return_value = model.IsYes(expected)
        g = game.Game(None, None, None, None, None)
        actual = players.will_hit_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    
    @patch('blackjack.game.BaseUI.input')
    def test_stand(self, mock_input):
        """When the user chooses to hit, will_hit_user() returns 
        False.
        """
        expected = False
        
        mock_input.return_value = model.IsYes(expected)
        g = game.Game(None, None, None, None, None)
        actual = players.will_hit_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    

class will_split_alwaysTestCase(unittest.TestCase):
    def test_paramters(self):
        """Functions that follow the will_split protocol should 
        accept the following parameters: hand, player, dealer, 
        playerlist.
        """
        hand = cards.Hand()
        player = players.Player((hand,), 'John Cleese')
        g = game.Game()
        player.will_split = partial(players.will_split_always, None)
        player.will_split(hand, g)
        
        # The test was that no exception was raised when will_split 
        # was called.
        self.assertTrue(True)
    
    def test_always_true(self):
        """will_split_always() should return True."""
        hand = cards.Hand()
        player = players.Player((hand,), 'John Cleese')
        player.will_split = partial(players.will_split_always, None)
        actual = player.will_split(hand, None)
        
        self.assertTrue(actual)


class will_split_recommendedTestCase(unittest.TestCase):
    def test_split_ace_or_8(self):
        """Always split aces or eights."""
        expected = True
        
        hand = cards.Hand([
            cards.Card(1, 2),
            cards.Card(1, 1),
        ])
        player = players.Player((hand,), 'Graham')
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual = players.will_split_recommended(player, hand, g)
        
        self.assertEqual(expected, actual)
        
    def test_split_4_5_or_8(self):
        """Never split fours, fives, or eights."""
        expected = False
        
        hand = cards.Hand([
            cards.Card(10, 2),
            cards.Card(10, 1),
        ])
        player = players.Player((hand,), 'Graham')
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual = players.will_split_recommended(player, hand, g)
        
        self.assertEqual(expected, actual)
    
    def test_split_2_3_or_7(self):
        """Split twos, threes, and sevens if the dealer's card is 
        seven or less.
        """
        expected1 = True
        expected2 = False
        
        hand = cards.Hand([
            cards.Card(2, 2),
            cards.Card(2, 1),
        ])
        player = players.Player((hand,), 'Graham')
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual1 = players.will_split_recommended(player, hand, g)
        
        self.assertEqual(expected1, actual1)
        
        hand = cards.Hand([
            cards.Card(2, 2),
            cards.Card(2, 1),
        ])
        player = players.Player((hand,), 'Graham')
        dhand = cards.Hand([
            cards.Card(8, 3),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual2 = players.will_split_recommended(player, hand, g)
        
        self.assertEqual(expected2, actual2)
    
    def test_split_6(self):
        """Split sixes if dealer's card is two through six."""
        expected1 = True
        expected2 = False
        
        hand = cards.Hand([
            cards.Card(6, 2),
            cards.Card(6, 1),
        ])
        player = players.Player((hand,), 'Graham')
        dhand = cards.Hand([
            cards.Card(6, 3),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual1 = players.will_split_recommended(player, hand, g)
        
        self.assertEqual(expected1, actual1)
        
        hand = cards.Hand([
            cards.Card(6, 2),
            cards.Card(6, 1),
        ])
        player = players.Player((hand,), 'Graham')
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual2 = players.will_split_recommended(player, hand, g)
        
        self.assertEqual(expected2, actual2)


class will_split_userTestCase(unittest.TestCase):
    @patch('blackjack.game.BaseUI.input')
    def test_split(self, mock_input):
        """When the user chooses to split, will_split_user() returns 
        True.
        """
        expected = True
        
        mock_input.return_value = model.IsYes(expected)
        g = game.Game(None, None, None, None, None)
        actual = players.will_split_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    
    @patch('blackjack.game.BaseUI.input')
    def test_stand(self, mock_input):
        """When the user chooses to split, will_split_user() returns 
        False.
        """
        expected = False
        
        mock_input.return_value = model.IsYes(expected)
        g = game.Game(None, None, None, None, None)
        actual = players.will_split_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    

class will_buyin_always(unittest.TestCase):
    def test_parameters(self):
        """Functions that follow the will_buyin protocol should 
        accept the following parameter: game.
        """
        player = players.Player()
        g = game.Game()
        
        player.will_buyin = partial(players.will_buyin_always, None)
        player.will_buyin(game)
        
        # The test was that no exception was raised when will_buyin 
        # was called.
        self.assertTrue(True)
    
    def test_always_true(self):
        """will_buyin_always() will always return True."""
        g = game.Game()
        p = players.Player()
        p.will_buyin = partial(players.will_buyin_always, None)
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


class will_double_down_recommendedTestCase(unittest.TestCase):
    def test_double_down_if_11(self):
        """If the player's hand is 11, player should double down."""
        expected = True
        
        phand = cards.Hand([
            cards.Card(5, 0),
            cards.Card(6, 0),
        ])
        player = players.Player((phand,), 'Terry')
        dhand = cards.Hand([
            cards.Card(11, 0),
            cards.Card(8, 3),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual = players.will_double_down_recommended(player, phand, g)
        
        self.assertEqual(expected, actual)
    
    def test_double_down_on_10(self):
        """If player's hand is 10 and the dealer's card is a 9 or 
        less, the player should double down.
        """
        expected = True
        
        phand = cards.Hand([
            cards.Card(4, 0),
            cards.Card(6, 0),
        ])
        player = players.Player((phand,), 'Terry')
        dhand = cards.Hand([
            cards.Card(9, 0),
            cards.Card(8, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual = players.will_double_down_recommended(player, phand, g)
        
        self.assertEqual(expected, actual)
    
    def test_not_double_down_on_10_dealer_10_or_1(self):
        """If the player's hand is 10 and the dealer's card is a 10 or 
        an ace, the player should not double down.
        """
        expected = False
        
        phand = cards.Hand([
            cards.Card(4, 0),
            cards.Card(6, 0),
        ])
        player = players.Player((phand,), 'Terry')
        dhand = cards.Hand([
            cards.Card(11, 0),
            cards.Card(8, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual = players.will_double_down_recommended(player, phand, g)
        
        self.assertEqual(expected, actual)
        
        expected = False
        
        phand = cards.Hand([
            cards.Card(4, 0),
            cards.Card(6, 0),
        ])
        player = players.Player((phand,), 'Terry')
        dhand = cards.Hand([
            cards.Card(11, 0),
            cards.Card(8, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual = players.will_double_down_recommended(player, phand, g)
        
        self.assertEqual(expected, actual)
    
    def test_double_down_on_9(self):
        """If player's hand is 9 and the dealer's card is a 2-6, the
         player should double down.
        """
        expected = True
        
        phand = cards.Hand([
            cards.Card(4, 0),
            cards.Card(5, 0),
        ])
        player = players.Player((phand,), 'Terry')
        dhand = cards.Hand([
            cards.Card(6, 0),
            cards.Card(8, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual = players.will_double_down_recommended(player, phand, g)
        
        self.assertEqual(expected, actual)
    
    def test_double_down_on_10(self):
        """If player's hand is 10 and the dealer's card is a 9 or 
        less, the player should double down.
        """
        expected = False
        
        phand = cards.Hand([
            cards.Card(4, 0),
            cards.Card(5, 0),
        ])
        player = players.Player((phand,), 'Terry')
        dhand = cards.Hand([
            cards.Card(1, 0),
            cards.Card(8, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual = players.will_double_down_recommended(player, phand, g)
        
        self.assertEqual(expected, actual)
        
        expected = False
        
        phand = cards.Hand([
            cards.Card(4, 0),
            cards.Card(5, 0),
        ])
        player = players.Player((phand,), 'Terry')
        dhand = cards.Hand([
            cards.Card(7, 0),
            cards.Card(8, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Game(None, dealer, (player,), None, None)
        actual = players.will_double_down_recommended(player, phand, g)
        
        self.assertEqual(expected, actual)


class will_double_down_userTestCase(unittest.TestCase):
    @patch('blackjack.game.BaseUI.input')
    def test_double_down(self, mock_input):
        """When the user chooses to double down, 
        will_double_down_user() returns True.
        """
        expected = True
        
        mock_input.return_value = model.IsYes(expected)
        g = game.Game(None, None, None, None, None)
        actual = players.will_double_down_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    
    @patch('blackjack.game.BaseUI.input')
    def test_not_double_down(self, mock_input):
        """When the user chooses to double down, 
        will_double_down_user() returns False.
        """
        expected = False
        
        mock_input.return_value = model.IsYes(expected)
        g = game.Game(None, None, None, None, None)
        actual = players.will_double_down_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    

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
