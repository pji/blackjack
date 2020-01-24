"""
test_players.py
~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.players module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from copy import copy
from functools import partial
import inspect
from types import MethodType
import unittest as ut
from unittest.mock import Mock, patch

from blackjack import cards, cli,   players, game, model


class PlayerTestCase(ut.TestCase):
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
    
    def test_asdict(self):
        """When called, asdict() should serialize the object to a 
        dictionary.
        """
        hands = (cards.Hand((
                cards.Card(11, 3),
                cards.Card(2, 1),
            )),)
        exp = {
            'class': 'Player',
            'chips': 200,
            'hands': hands,
            'insured': 0,
            'name': 'spam',
            'will_buyin': 'will_buyin_always',
            'will_double_down': 'will_double_down_always',
            'will_hit': 'will_hit_dealer',
            'will_insure': 'will_insure_always',
            'will_split': 'will_split_always',
        }
        
        player = players.Player(hands, 'spam', 200)
        player.will_buyin = MethodType(players.will_buyin_always, player)
        player.will_double_down = MethodType(players.will_double_down_always, 
                                             player)
        player.will_hit = MethodType(players.will_hit_dealer, player)
        player.will_insure = MethodType(players.will_insure_always, player)
        player.will_split = MethodType(players.will_split_always, player)
        act = player.asdict()
        
        self.assertEqual(exp, act)
    
    def test_fromdict(self):
        """Given a dictionary as created by asdict(), fromdict() 
        should deserialize the Player object.
        """
        hands = (cards.Hand((
                cards.Card(11, 3),
                cards.Card(2, 1),
            )),)
        exp = players.Player(hands, 'spam', 200)
        exp.will_buyin = MethodType(players.will_buyin_always, exp)
        exp.will_double_down = MethodType(players.will_double_down_always, exp)
        exp.will_hit = MethodType(players.will_hit_dealer, exp)
        exp.will_insure = MethodType(players.will_insure_always, exp)
        exp.will_split = MethodType(players.will_split_always, exp)
        
        value = {
            'class': 'Player',
            'chips': 200,
            'hands': hands,
            'insured': 0,
            'name': 'spam',
            'will_buyin': 'will_buyin_always',
            'will_double_down': 'will_double_down_always',
            'will_hit': 'will_hit_dealer',
            'will_insure': 'will_insure_always',
            'will_split': 'will_split_always',
        }
        act = players.Player.fromdict(value)
        
        self.assertEqual(exp, act)
    
    def test_fromdict_methods(self):
        """Given a dictionary as created by asdict(), fromdict() 
        should deserialize the Player object.
        """
        exp = MethodType
        
        hands = (cards.Hand((
                cards.Card(11, 3),
                cards.Card(2, 1),
            )),)
        value = {
            'class': 'Player',
            'chips': 200,
            'hands': hands,
            'insured': 0,
            'name': 'spam',
            'will_buyin': 'will_buyin_always',
            'will_double_down': 'will_double_down_always',
            'will_hit': 'will_hit_dealer',
            'will_insure': 'will_insure_always',
            'will_split': 'will_split_always',
        }
        methods = [key for key in value if key.startswith('will_')]
        player = players.Player.fromdict(value)        
        for method in methods:
            act = getattr(player, method)
            
            self.assertIsInstance(act, exp)
    
    def test_fromdict_invalid_method(self):
        """Given a dictionary as created by asdict(), fromdict() 
        should deserialize the Player object.
        """
        exp = ValueError
        
        hands = (cards.Hand((
                cards.Card(11, 3),
                cards.Card(2, 1),
            )),)
        dict_ = {
            'class': 'Player',
            'chips': 200,
            'hands': hands,
            'insured': 0,
            'name': 'spam',
            'will_buyin': 'will_buyin_always',
            'will_double_down': 'will_double_down_always',
            'will_hit': 'will_hit_dealer',
            'will_insure': 'will_insure_always',
            'will_split': 'will_split_always',
        }
        methkeys = [key for key in dict_ if key.startswith('will_')]
        test = 'spam'
        for key in methkeys:
            test_dict = copy(dict_)
            test_dict[key] = test
            
            with self.assertRaises(exp):
                act = players.Player.fromdict(test_dict)

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
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
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
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(5, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
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
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
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
        player = players.Player((phand,), 'John')
        dhand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(2, 3, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, (player,), None, 20)
        actual = players.will_hit_recommended(None, phand, g)
        
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
        actual = players.will_hit_recommended(None, phand, g)
        
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
        actual = players.will_hit_recommended(None, phand, g)
        
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
        actual = players.will_hit_user(None, None, g)
        
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
        actual = players.will_hit_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    

class will_split_alwaysTestCase(ut.TestCase):
    def test_paramters(self):
        """Functions that follow the will_split protocol should 
        accept the following parameters: hand, player, dealer, 
        playerlist.
        """
        hand = cards.Hand()
        player = players.Player((hand,), 'John Cleese')
        g = game.Engine()
        method = MethodType(players.will_split_always, player)
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
        g = game.Engine(None, dealer, (player,), None, None)
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
        g = game.Engine(None, dealer, (player,), None, None)
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
        g = game.Engine(None, dealer, (player,), None, None)
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
        g = game.Engine(None, dealer, (player,), None, None)
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual2 = players.will_split_recommended(player, hand, g)
        
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
        actual = players.will_split_user(None, None, g)
        
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
        actual = players.will_split_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    

class will_buyin_always(ut.TestCase):
    def test_parameters(self):
        """Functions that follow the will_buyin protocol should 
        accept the following parameter: game.
        """
        player = players.Player()
        g = game.Engine()
        
        player.will_buyin = partial(players.will_buyin_always, None)
        player.will_buyin(game)
        
        # The test was that no exception was raised when will_buyin 
        # was called.
        self.assertTrue(True)
    
    def test_always_true(self):
        """will_buyin_always() will always return True."""
        g = game.Engine()
        p = players.Player()
        p.will_buyin = partial(players.will_buyin_always, None)
        actual = p.will_buyin(g)
        
        self.assertTrue(actual)


class will_double_down_alwaysTestCase(ut.TestCase):
    def test_parameters(self):
        """Functions that follow the will_double_down protocol should 
        accept the following parameters: self, hand, game.
        """
        player = players.Player()
        hand = cards.Hand()
        g = game.Engine()
        
        _ = players.will_double_down_always(player, hand, game)
        
        # The test was that no exception was raised when will_buyin 
        # was called.
        self.assertTrue(True)
    
    def test_always_true(self):
        """will_double_down_always() will always return True."""
        g = game.Engine()
        h = cards.Hand()
        p = players.Player()
        actual = players.will_double_down_always(p, h, g)
        
        self.assertTrue(actual)


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
        g = game.Engine(None, dealer, (player,), None, None)
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
        g = game.Engine(None, dealer, (player,), None, None)
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
        g = game.Engine(None, dealer, (player,), None, None)
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
        g = game.Engine(None, dealer, (player,), None, None)
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
        g = game.Engine(None, dealer, (player,), None, None)
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
        g = game.Engine(None, dealer, (player,), None, None)
        actual = players.will_double_down_recommended(player, phand, g)
        
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
        actual = players.will_double_down_user(None, None, g)
        
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
        actual = players.will_double_down_user(None, None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    

class will_insure_alwaysTestCase(ut.TestCase):
    def test_parameters(self):
        """Functions that follow the will_insure protocol should 
        accept the following parameters: self, hand, game.
        """
        player = players.Player()
        hand = cards.Hand()
        g = game.Engine()
        
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
        g = game.Engine(None, None, (p,), None, 20)
        actual = players.will_insure_always(p, g)
        
        self.assertEqual(expected, actual)


class will_insure_neverTestCase(ut.TestCase):
    def test_parameters(self):
        """Functions that follow the will_insure protocol should 
        accept the following parameters: self, game.
        """
        player = players.Player()
        hand = cards.Hand()
        g = game.Engine()
        
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
        g = game.Engine(None, None, (p,), None, 20)
        actual = players.will_insure_always(p, g)
        
        self.assertEqual(expected, actual)


class will_insure_userTestCase(ut.TestCase):
    @patch('blackjack.game.BaseUI.insure_prompt')
    def test_insure(self, mock_input):
        """When the user chooses to double down, 
        will_insure_user() returns True.
        """
        expected = 10
        
        mock_input.return_value = model.IsYes('y')
        g = game.Engine(None, None, None, None, expected * 2)
        actual = players.will_insure_user(None, g)
        
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
        actual = players.will_insure_user(None, g)
        
        mock_input.assert_called()
        self.assertEqual(expected, actual)
    

class playerfactoryTestCase(ut.TestCase):
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


class make_playerTestCase(ut.TestCase):
    def test_returns_Player(self):
        """The make_player() function returns an instance of a Player 
        subclass.
        """
        expected = players.Player
        actual = players.make_player()
        self.assertTrue(isinstance(actual, expected))
    
    @patch('blackjack.players.get_name')
    def test_player_has_name(self, mock_get_name):
        """The players created by make_player() have names."""
        expected = 'Graham'
        
        mock_get_name.return_value = 'Graham'
        player = players.make_player()
        actual = player.name
        
        self.assertEqual(expected, actual)
    
    def test_has_decision_methods(self):
        """The players created by make_player() should have the 
        decision methods for Players, such as will_hit and 
        will_insure.
        """
        # As long as no exception is raised, this test passes.
        phand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 2),
        ])
        dhand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 2),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        g = game.Engine(None, dealer, None, None, 0)
        player = players.make_player()
        
        methods = [
            player.will_hit,
            player.will_split,
#             player.will_double_down,
        ]
        for method in methods:
            _ = method(phand, g)
        
        methods = [
            player.will_buyin,
            player.will_insure,
        ]
        for method in methods:
            _ = method(g)
    
    def test_random_chips(self):
        """Given a bet, make_player() should give the player a random 
        number of chips based on that bet.
        """
        exp_high = 21
        exp_low = 1
        
        player = players.make_player(bet=1)
        actual = player.chips
        
        self.assertTrue(exp_high >= actual)
        self.assertTrue(exp_low <= actual)


class name_builderTestCase(ut.TestCase):
    def test_construct_name(self):
        """Given a beginning, middle, and end, name_builder should 
        return a string that is the combination of the three strings.
        """
        expected = 'Jichael'
        
        beginning = 'John'
        end = 'Michael'
        actual = players.name_builder(beginning, end)
        
        self.assertEqual(expected, actual)
        
    def test_end_starts_with_vowel(self):
        """If the middle string starts with a vowel and the beginning 
        string does not, the first character of the beginning string 
        should be put in front of the middle string rather than 
        replacing the first letter of the middle string.
        """
        expected = 'Meric'
        
        beginning = 'Michael'
        end = 'Eric'
        actual = players.name_builder(beginning, end)
        
        self.assertEqual(expected, actual)
    
    def test_end_starts_with_two_or_more_consonants(self):
        """If the middle string starts with two or more consonants 
        and the beginning string starts with at least one consonant, 
        the first consonants of the middle string should be replaced 
        with the first consonants of the beginning string.
        """
        expected = 'Bristopher'
        
        beginning = 'Brian'
        end = 'Christopher'
        actual = players.name_builder(beginning, end)
        
        self.assertEqual(expected, actual)
    
    def test_end_and_start_start_with_vowels(self):
        """If the end string and the start string start with vowels, 
        the starting vowels of the end should be replaced with the 
        starting vowels of the start.
        """
        expected = 'Emy'
        
        start = 'Eric'
        end = 'Amy'
        actual = players.name_builder(start, end)
        
        self.assertEqual(expected, actual)
    
    def test_end_starts_with_two_or_more_consonants(self):
        """If the end string starts with two or more consonants 
        and the beginning string starts with at least one vowel, 
        the first vowels of the beginning string should be placed 
        before the first letter of the end string.
        """
        expected = 'Ejohn'
        
        beginning = 'Eric'
        end = 'John'
        actual = players.name_builder(beginning, end)
        
        self.assertEqual(expected, actual)
    

class get_chipsTestCase(ut.TestCase):
    def test_accepts_bet(self):
        """The get_chips() function should accept the initial buyin 
        value for a game of blackjack.
        """
        expected = 20
        
        # This is the test. It fails if an exception is raised.
        _ = players.get_chips(expected)
    
    def test_returns_chips(self):
        """get_chips should return a number of chips that is between 
        1 and 21 times the given bet.
        """
        exp_high = 21
        exp_low = 1
        
        bet = 1
        actual = players.get_chips(bet)
        
        self.assertTrue(exp_high >= actual)
        self.assertTrue(exp_low <= actual)

