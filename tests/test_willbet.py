"""
test_willbet.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willbet module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from types import MethodType
import unittest as ut
from unittest.mock import patch

from blackjack import players, game, willbet


class WillBetTestCase(ut.TestCase):
    def setUp(self):
        self.engine = game.Engine()
        self.player = players.Player(chips=1000)

    def returned_value_test(self, fn, exp):
        # Test data and state.
        self.player.will_bet = MethodType(fn, self.player)

        # Run test.
        act = self.player.will_bet(self.engine)

        # Determine test result.
        self.assertEqual(exp, act)


# Test cases.
class WillBetDealerTestCase(WillBetTestCase):
    def test_will_raise_error(self):
        """When called as the will_bet method of a Player object
        with a game.Engine, will_bet_dealer will raise a TypeError.
        """
        # Expected value.
        exp_ex = TypeError
        exp_msg = 'Dealer cannot bet.'

        # Test data.
        fn = willbet.will_bet_dealer

        # Run test and determine result.
        with self.assertRaisesRegex(exp_ex, exp_msg):
            self.returned_value_test(fn, None)


class WillBetMaxTestCase(WillBetTestCase):
    def test_will_always_return_maximum_bet(self):
        """When called as the will_bet method of a Player object
        with a game.Engine, will_bet_max will return the maximum
        bet allowed by the game.
        """
        exp = self.engine.bet_max
        fn = willbet.will_bet_max
        self.returned_value_test(fn, exp)

    def test_will_not_bet_more_chips_than_has(self):
        """If the maximum bet is higher than the amount the player
        has, the player will bet all their remaining chips.
        """
        exp = 96
        self.player.chips = exp
        fn = willbet.will_bet_max
        self.returned_value_test(fn, exp)


class WillBetMinTestCase(WillBetTestCase):
    def test_will_always_return_maximum_bet(self):
        """When called as the will_bet method of a Player object
        with a game.Engine, will_bet_min will return the minimum
        bet allowed by the game.
        """
        exp = self.engine.bet_min
        fn = willbet.will_bet_min
        self.returned_value_test(fn, exp)


class WillBetNeverTestCase(WillBetTestCase):
    def test_will_always_return_zero(self):
        """When called as the will_bet method of a Player object
        with a game.Engine, will_bet_never will return zero.
        """
        exp = 0
        fn = willbet.will_bet_never
        self.returned_value_test(fn, exp)


class WillBetRandomTestCase(WillBetTestCase):
    @patch('blackjack.willbet.randrange', return_value=125)
    def test_will_return_a_random_number(self, mock_randrange):
        """When called as the will_bet method of a Player object
        with a game.Engine, will_bet_random will return a random
        number between the minimum and maximum bet.
        """
        exp = mock_randrange()
        fn = willbet.will_bet_random
        self.returned_value_test(fn, exp)
