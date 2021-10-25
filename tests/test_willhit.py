"""
test_willhit.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willhit module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import inspect
import unittest as ut
from unittest.mock import call, Mock, patch

from blackjack import cards, cli, players, game, model, willhit


class will_hit_dealerTestCase(ut.TestCase):
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
        g = game.Engine()
        _ = willhit.will_hit_dealer(player, hand, g)

    def test_stand_on_bust(self):
        """If the hand is bust, will_hit_dealer() should return
        False.
        """
        expected = willhit.STAND

        h = cards.Hand([
            cards.Card(11, 0),
            cards.Card(4, 2),
            cards.Card(11, 3),
        ])
        actual = willhit.will_hit_dealer(None, h)

        self.assertEqual(expected, actual)

    def test_stand_on_17_plus(self):
        """If the score of the hand is 17 or greater, will_hit_dealer()
        should return False.
        """
        expected = willhit.STAND

        h1 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(7, 2),
        ])
        h2 = cards.Hand([
            cards.Card(12, 1),
            cards.Card(2, 3),
            cards.Card(8, 1),
        ])
        actual_h1 = willhit.will_hit_dealer(None, h1)
        actual_h2 = willhit.will_hit_dealer(None, h2)

        self.assertEqual(expected, actual_h1)
        self.assertEqual(expected, actual_h2)

    def test_hit_on_less_than_17(self):
        """If the score of the hand is less than 17, will_hit_dealer()
        should return true.
        """
        expected = willhit.HIT

        h1 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(6, 2),
        ])
        h2 = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3),
            cards.Card(8, 1),
        ])
        actual_h1 = willhit.will_hit_dealer(None, h1)
        actual_h2 = willhit.will_hit_dealer(None, h2)

        self.assertEqual(expected, actual_h1)


class will_hit_neverTestCase(ut.TestCase):
    def test_stand(self):
        """will_hit_never() should never return True."""
        expected = False

        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(11, 2),
        ])
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(5, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
        actual = willhit.will_hit_never(None, phand, g)

        self.assertEqual(expected, actual)


class will_hit_randomTestCase(ut.TestCase):
    @patch('blackjack.willhit.choice', return_value=True)
    def test_random_hit(self, mock_choice):
        """When called, will_hit_random() should call random.choice()
        and return the result.
        """
        exp_result = True
        exp_call = call([True, False])

        act_result = willhit.will_hit_random(None, None, None)
        act_call = mock_choice.mock_calls[-1]

        self.assertEqual(exp_result, act_result)
        self.assertEqual(exp_call, act_call)


class will_hit_recommendedTestCase(ut.TestCase):
    def test_dealer_card_good_hit_if_not_17(self):
        """If the dealer's up card is 7-11, the player should hit
        until their hand's total is 17 or greater.
        """
        expected = True

        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(6, 2),
        ])
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
        actual = willhit.will_hit_recommended(None, phand, g)

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
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
        actual = willhit.will_hit_recommended(None, phand, g)

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
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(5, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
        actual = willhit.will_hit_recommended(None, phand, g)

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
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
        actual = willhit.will_hit_recommended(None, phand, g)

        self.assertEqual(expected, actual)

    def test_do_not_hit_soft_19(self):
        """If the player's hand is a soft 19, don't hit."""
        expected = False

        phand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(6, 2),
            cards.Card(2, 2),
        ])
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
        actual = willhit.will_hit_recommended(None, phand, g)

        self.assertEqual(expected, actual)

    def test_stand(self):
        """If the situation doesn't match the above criteria, stand."""
        expected = False

        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(11, 2),
        ])
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(5, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
        actual = willhit.will_hit_recommended(None, phand, g)

        self.assertEqual(expected, actual)

    def test_stand_bust(self):
        """If the hand is bust, stand."""
        expected = False

        phand = cards.Hand((
            cards.Card(8, 2),
            cards.Card(6, 1),
            cards.Card(2, 1),
            cards.Card(7, 2),
        ))
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(5, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
        actual = willhit.will_hit_recommended(None, phand, g)

        self.assertEqual(expected, actual)


class will_hit_userTestCase(ut.TestCase):
    @patch('blackjack.game.BaseUI.hit_prompt')
    def test_hit(self, mock_input):
        """When the user chooses to hit, will_hit_user() returns
        True.
        """
        expected = True

        mock_input.return_value = model.IsYes(expected)
        ui = cli.TableUI()
        g = game.Engine(None, None, None, None, None)
        actual = willhit.will_hit_user(None, None, g)

        mock_input.assert_called()
        self.assertEqual(expected, actual)

    @patch('blackjack.game.BaseUI.hit_prompt')
    def test_stand(self, mock_input):
        """When the user chooses to hit, will_hit_user() returns
        False.
        """
        expected = False

        mock_input.return_value = model.IsYes(expected)
        ui = cli.TableUI()
        g = game.Engine(None, None, None, None, None)
        actual = willhit.will_hit_user(None, None, g)

        mock_input.assert_called()
        self.assertEqual(expected, actual)
