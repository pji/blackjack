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
import json
from types import MethodType
import unittest as ut
from unittest.mock import Mock, patch

from blackjack import cards, cli, players, game, model


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
    
    def test_deserialize(self):
        """When given a Player serialized as a JSON string, 
        deserialize() should return the deserialized instance 
        of Player.
        """
        hands = (cards.Hand((
                cards.Card(11, 3),
                cards.Card(2, 1),
            )),)
        exp = players.Player(hands, 'spam', 200)
        exp.will_buyin = MethodType(players.will_buyin_always, exp)
        exp.will_double_down = MethodType(players.will_double_down_always, 
                                             exp)
        exp.will_hit = MethodType(players.will_hit_dealer, exp)
        exp.will_insure = MethodType(players.will_insure_always, exp)
        exp.will_split = MethodType(players.will_split_always, exp)
        
        serial = exp.serialize()
        act = players.Player.deserialize(serial)
        
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
    
    def test__asdict(self):
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
        act = player._asdict()
        
        self.assertEqual(exp, act)
    
    def test_serialize(self):
        """When called, serialize() should return the object 
        serialized as a JSON string.
        """
        hands = (cards.Hand((
                cards.Card(11, 3),
                cards.Card(2, 1),
            )),)
        exp = json.dumps({
            'class': 'Player',
            'chips': 200,
            'hands': (hands[0].serialize(),),
            'insured': 0,
            'name': 'spam',
            'will_buyin': 'will_buyin_always',
            'will_double_down': 'will_double_down_always',
            'will_hit': 'will_hit_dealer',
            'will_insure': 'will_insure_always',
            'will_split': 'will_split_always',
        })
        
        player = players.Player(hands, 'spam', 200)
        player.will_buyin = MethodType(players.will_buyin_always, player)
        player.will_double_down = MethodType(players.will_double_down_always, 
                                             player)
        player.will_hit = MethodType(players.will_hit_dealer, player)
        player.will_insure = MethodType(players.will_insure_always, player)
        player.will_split = MethodType(players.will_split_always, player)
        act = player.serialize()
        
        self.assertEqual(exp, act)


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


class validate_player_or_noneTestCase(ut.TestCase):
    def test_valid(self):
        """Given a Player object, validate_player() should return it."""
        exp = players.Player(name='spam')
        
        class Eggs:
            msg = '{}'
        act = players.validate_player_or_none(Eggs(), exp)
        
        self.assertEqual(exp, act)
    
    def test_invalid(self):
        """Given a non-Player object, validate_player() should raise a 
        ValueError exception.
        """
        exp = ValueError
        
        value = 0
        class Spam():
            msg = '{}'
        
        with self.assertRaises(exp):
            _ = players.validate_player_or_none(Spam(), value)
