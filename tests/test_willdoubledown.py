"""
test_willdoubledown.py
~~~~~~~~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.test_willdoubledown
module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from functools import partial
import inspect
import unittest as ut
from unittest.mock import call, Mock, patch

from blackjack import cards, cli, players, game, model, willdoubledown


class will_double_down_alwaysTestCase(ut.TestCase):
    def test_parameters(self):
        """Functions that follow the will_double_down protocol should
        accept the following parameters: self, hand, game.
        """
        player = players.Player()
        hand = cards.Hand()
        g = game.Engine()

        _ = willdoubledown.will_double_down_always(player, hand, game)

        # The test was that no exception was raised when will_buyin
        # was called.
        self.assertTrue(True)

    def test_always_true(self):
        """will_double_down_always() will always return True."""
        g = game.Engine()
        h = cards.Hand()
        p = players.Player()
        actual = willdoubledown.will_double_down_always(p, h, g)

        self.assertTrue(actual)


class will_double_down_neverTestCase(ut.TestCase):
    def test_never_double_down(self):
        """will_double_down_never should always return False."""
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willdoubledown.will_double_down_never(player, phand, g)

        self.assertEqual(expected, actual)


class will_double_down_randomTestCase(ut.TestCase):
    @patch('blackjack.willdoubledown.choice', return_value=True)
    def test_random_double_down(self, mock_choice):
        """When called, will_double_down_random() should call
        random.choice() and return the result.
        """
        exp_result = True
        exp_call = call([True, False])

        act_result = willdoubledown.will_double_down_random(None, None, None)
        act_call = mock_choice.mock_calls[-1]

        self.assertEqual(exp_result, act_result)
        self.assertEqual(exp_call, act_call)


class will_double_down_recommendedTestCase(ut.TestCase):
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willdoubledown.will_double_down_recommended(player, phand, g)

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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willdoubledown.will_double_down_recommended(player, phand, g)

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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willdoubledown.will_double_down_recommended(player, phand, g)

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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willdoubledown.will_double_down_recommended(player, phand, g)

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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willdoubledown.will_double_down_recommended(player, phand, g)

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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willdoubledown.will_double_down_recommended(player, phand, g)

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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = willdoubledown.will_double_down_recommended(player, phand, g)

        self.assertEqual(expected, actual)


class will_double_down_userTestCase(ut.TestCase):
    @patch('blackjack.game.BaseUI.doubledown_prompt')
    def test_double_down(self, mock_input):
        """When the user chooses to double down,
        will_double_down_user() returns True.
        """
        expected = True

        mock_input.return_value = model.IsYes(expected)
        g = game.Engine(None, None, None, None, None)
        actual = willdoubledown.will_double_down_user(None, None, g)

        mock_input.assert_called()
        self.assertEqual(expected, actual)

    @patch('blackjack.game.BaseUI.doubledown_prompt')
    def test_not_double_down(self, mock_input):
        """When the user chooses to double down,
        will_double_down_user() returns False.
        """
        expected = False

        mock_input.return_value = model.IsYes(expected)
        g = game.Engine(None, None, None, None, None)
        actual = willdoubledown.will_double_down_user(None, None, g)

        mock_input.assert_called()
        self.assertEqual(expected, actual)
