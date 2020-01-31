"""
test_willinsure.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willinsure module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import inspect
import unittest as ut
from unittest.mock import call, Mock, patch

from blackjack import cards, cli, players, game, model, willinsure


class will_insure_alwaysTestCase(ut.TestCase):
    def test_parameters(self):
        """Functions that follow the will_insure protocol should 
        accept the following parameters: self, hand, game.
        """
        player = players.Player()
        hand = cards.Hand()
        g = game.Engine()
        
        _ = willinsure.will_insure_always(player, g)
        
        # The test was that no exception was raised when will_buyin 
        # was called.
        self.assertTrue(True)
    
    def test_always_max(self):
        """will_double_down_always() will always return the maximum 
        bet, which is half of the game's buy in."""
        expected = 10
        
        h = cards.Hand()
        p = players.Player()
        g = game.Engine(None, None, (p,), None, 20)
        actual = willinsure.will_insure_always(p, g)
        
        self.assertEqual(expected, actual)


class will_insure_neverTestCase(ut.TestCase):
    def test_parameters(self):
        """Functions that follow the will_insure protocol should 
        accept the following parameters: self, game.
        """
        player = players.Player()
        hand = cards.Hand()
        g = game.Engine()
        
        _ = willinsure.will_insure_never(player, g)
        
        # The test was that no exception was raised when will_buyin 
        # was called.
        self.assertTrue(True)
    
    def test_always_zero(self):
        """will_double_down_always() will always return the maximum 
        bet, which is half of the game's buy in."""
        expected = 10
        
        h = cards.Hand()
        p = players.Player()
        g = game.Engine(None, None, (p,), None, 20)
        actual = willinsure.will_insure_always(p, g)
        
        self.assertEqual(expected, actual)


class will_insure_randomTestCase(ut.TestCase):
    @patch('blackjack.willinsure.choice', return_value=1)
    def test_random_insure(self, mock_choice):
        """When called, will_insure_random() should call 
        random.choice() and return the result.
        """
        exp_result = 1
        exp_call = call(range(0, 1))
        
        g = game.Engine(buyin=2)
        act_result = willinsure.will_insure_random(None, g)
        act_call = mock_choice.mock_calls[-1]
        
        self.assertEqual(exp_result, act_result)
        self.assertEqual(exp_call, act_call)


class will_insure_userTestCase(ut.TestCase):
    @patch('blackjack.game.BaseUI.insure_prompt')
    def test_insure(self, mock_input):
        """When the user chooses to double down, 
        will_insure_user() returns True.
        """
        expected = 10
        
        mock_input.return_value = model.IsYes('y')
        g = game.Engine(None, None, None, None, expected * 2)
        actual = willinsure.will_insure_user(None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    
    @patch('blackjack.game.BaseUI.insure_prompt')
    def test_not_insure(self, mock_input):
        """When the user chooses to double down, 
        will_insure_user() returns False.
        """
        expected = 0
        
        mock_input.return_value = model.IsYes('n')
        g = game.Engine(None, None, None, None, 20)
        actual = willinsure.will_insure_user(None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    

