"""
test_willbet.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.willbet module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from functools import partial
import unittest as ut

from blackjack import players, game, willbet


class WillBetTestCase(ut.TestCase):
    def setUp(self):
        self.engine = game.Engine()


# Test cases.
class WillBetMaxTestCase(WillBetTestCase):
    def test_will_always_return_maximum_bet(self):
        """When called as the will_bet method of a Player object
        with a game.Engine, will_bet_max will return the maximum
        bet allowed by the game.
        """
        # Expected value.
        exp = self.engine.bet_max

        # Test data and state.
        player = players.Player()
        player.will_bet = partial(willbet.will_bet_max, None)

        # Run test.
        act = player.will_bet(self.engine)

        # Determine test result.
        self.assertEqual(exp, act)
