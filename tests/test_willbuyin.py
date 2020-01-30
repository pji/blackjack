"""
test_willbuyin.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willbuyin module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from functools import partial
import inspect
import unittest as ut
from unittest.mock import Mock, patch

from blackjack import cards, cli, players, game, model, willbuyin


class will_buyin_always(ut.TestCase):
    def test_parameters(self):
        """Functions that follow the will_buyin protocol should 
        accept the following parameter: game.
        """
        player = players.Player()
        g = game.Engine()
        
        player.will_buyin = partial(willbuyin.will_buyin_always, None)
        player.will_buyin(game)
        
        # The test was that no exception was raised when will_buyin 
        # was called.
        self.assertTrue(True)
    
    def test_always_true(self):
        """will_buyin_always() will always return True."""
        g = game.Engine()
        p = players.Player()
        p.will_buyin = partial(willbuyin.will_buyin_always, None)
        actual = p.will_buyin(g)
        
        self.assertTrue(actual)


class will_buyin_never(ut.TestCase):
    def test_never_buyin(self):
        exp = False
        act = willbuyin.will_buyin_never(None, None)
        self.assertEqual(exp, act)


