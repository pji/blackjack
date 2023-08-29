"""
test_willdoubledown.py
~~~~~~~~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.test_willdoubledown
module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import inspect
import unittest as ut
from functools import partial
from random import seed
from unittest.mock import call, Mock, patch

import pytest

from blackjack import cards, cli, players, game, model
from blackjack import willdoubledown as wdd
from tests.common import engine, hand, player


# Tests cases.
@pytest.mark.hand([3, 1], [4, 2])
@pytest.mark.will('will_double_down', wdd.will_double_down_always)
def test_will_double_down_always(engine, hand, player):
    """When called as the will_double_down
    method of a :class:`Player` object with
    a :class:`game.Engine`, :func:`willbet.will_double_down_always`
    will always double down.
    """
    assert player.will_double_down(hand, game)


@pytest.mark.hand([3, 1], [4, 2])
@pytest.mark.will('will_double_down', wdd.will_double_down_never)
def test_will_double_down_never(engine, hand, player):
    """When called as the will_double_down
    method of a :class:`Player` object with
    a :class:`game.Engine`,
    :func:`willbet.will_double_down_never`
    will never double down.
    """
    assert not player.will_double_down(hand, game)


@pytest.mark.hand([3, 1], [4, 2])
@pytest.mark.will('will_double_down', wdd.will_double_down_random)
def test_will_double_down_random(engine, hand, player):
    """When called as the will_double_down
    method of a :class:`Player` object with
    a :class:`game.Engine`,
    :func:`willbet.will_double_down_random`
    will randomly double down.
    """
    seed('spam')
    assert player.will_double_down(hand, game)
    assert not player.will_double_down(hand, game)
    assert player.will_double_down(hand, game)


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
        actual = wdd.will_double_down_recommended(player, phand, g)

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
        actual = wdd.will_double_down_recommended(player, phand, g)

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
        actual = wdd.will_double_down_recommended(player, phand, g)

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
        actual = wdd.will_double_down_recommended(player, phand, g)

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
        actual = wdd.will_double_down_recommended(player, phand, g)

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
        actual = wdd.will_double_down_recommended(player, phand, g)

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
        actual = wdd.will_double_down_recommended(player, phand, g)

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
        actual = wdd.will_double_down_user(None, None, g)

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
        actual = wdd.will_double_down_user(None, None, g)

        mock_input.assert_called()
        self.assertEqual(expected, actual)
