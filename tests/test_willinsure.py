"""
test_willinsure.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willinsure module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import inspect
from types import MethodType
import unittest as ut
from unittest.mock import call, Mock, patch

from blackjack import cards, cli, players, game, model, willinsure


class WillInsureTestCase(ut.TestCase):
    def setUp(self):
        self.engine = game.Engine()
        self.player = players.Player(chips=1000)
        self.player.bet = 50

    def returned_value_test(self, fn, exp):
        # Test data and state.
        self.player.will_insure = MethodType(fn, self.player)

        # Run test.
        act = self.player.will_insure(self.engine)

        # Determine test result.
        self.assertEqual(exp, act)


# Test cases.
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
        """will_insure_always() will always return the maximum
        insurance, which is half their bet."""
        expected = 10

        h = cards.Hand()
        p = players.Player()
        p.will_insure = MethodType(willinsure.will_insure_always, p)
        g = game.Engine(None, None, (p,), None, 30)
        p.bet = expected * 2
        actual = p.will_insure(g)

        self.assertEqual(expected, actual)


class will_insure_neverTestCase(ut.TestCase):
    def test_always_zero(self):
        """will_insure_always() will always return the maximum
        bet, which is half of the game's buy in."""
        expected = 0

        h = cards.Hand()
        p = players.Player()
        g = game.Engine(None, None, (p,), None, 20)
        actual = willinsure.will_insure_never(p, g)

        self.assertEqual(expected, actual)


class will_insure_randomTestCase(ut.TestCase):
    @patch('blackjack.willinsure.choice', return_value=1)
    def test_random_insure(self, mock_choice):
        """When called, will_insure_random() should call
        random.choice() and return the result.
        """
        # Expected values.
        exp_result = 1
        exp_call = call(range(0, exp_result))

        # Test data and state.
        g = game.Engine(buyin=4)
        p = players.Player()
        p.bet = exp_result * 2
        p.will_insure = MethodType(willinsure.will_insure_random, p)

        # Run test and gather actuals.
        act_result = p.will_insure(g)
        act_call = mock_choice.mock_calls[-1]

        # Determine test success.
        self.assertEqual(exp_result, act_result)
        self.assertEqual(exp_call, act_call)


class will_insure_userTestCase(WillInsureTestCase):
    @patch('blackjack.game.BaseUI.insure_prompt', return_value=model.Bet(20))
    def test_insure(self, mock_input):
        """When the user chooses to insure,
        will_insure_user() returns the insured amount.
        """
        exp = mock_input().value
        fn = willinsure.will_insure_user
        self.returned_value_test(fn, exp)

        # Special test for input prompt.
        exp_call = call(self.player.bet // 2)
        act_call = mock_input.mock_calls[-1]
        self.assertEqual(exp_call, act_call)
