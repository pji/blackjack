"""
test_willsplit.py
~~~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willsplit module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from functools import partial
import inspect
from types import MethodType
import unittest as ut
from unittest.mock import Mock, patch

from blackjack import cards, cli, players, game, model, willsplit


class will_split_alwaysTestCase(ut.TestCase):
    def test_paramters(self):
        """Functions that follow the will_split protocol should 
        accept the following parameters: hand, player, dealer, 
        playerlist.
        """
        hand = cards.Hand()
        player = players.Player((hand,), 'John Cleese')
        g = game.Engine()
        method = MethodType(willsplit.will_split_always, player)
        player.will_split = partial(willsplit.will_split_always, None)
        player.will_split(hand, g)
        
        # The test was that no exception was raised when will_split 
        # was called.
        self.assertTrue(True)
    
    def test_always_true(self):
        """will_split_always() should return True."""
        hand = cards.Hand()
        player = players.Player((hand,), 'John Cleese')
        player.will_split = partial(willsplit.will_split_always, None)
        actual = player.will_split(hand, None)
        
        self.assertTrue(actual)


class will_split_neverTestCase(ut.TestCase):
    def test_never_split(self):
        """will_split_never() should return False."""
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willsplit.will_split_never(player, hand, g)
        
        self.assertEqual(expected, actual)


class will_split_recommendedTestCase(ut.TestCase):
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willsplit.will_split_recommended(player, hand, g)
        
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willsplit.will_split_recommended(player, hand, g)
        
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual1 = willsplit.will_split_recommended(player, hand, g)
        
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual2 = willsplit.will_split_recommended(player, hand, g)
        
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual1 = willsplit.will_split_recommended(player, hand, g)
        
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual2 = willsplit.will_split_recommended(player, hand, g)
        
        self.assertEqual(expected2, actual2)


class will_split_userTestCase(ut.TestCase):
    @patch('blackjack.game.BaseUI.split_prompt')
    def test_split(self, mock_input):
        """When the user chooses to split, will_split_user() returns 
        True.
        """
        expected = True
        
        mock_input.return_value = model.IsYes(expected)
        g = game.Engine(None, None, None, None, None)
        actual = willsplit.will_split_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    
    @patch('blackjack.game.BaseUI.split_prompt')
    def test_stand(self, mock_input):
        """When the user chooses to split, will_split_user() returns 
        False.
        """
        expected = False
        
        mock_input.return_value = model.IsYes(expected)
        g = game.Engine(None, None, None, None, None)
        actual = willsplit.will_split_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    

