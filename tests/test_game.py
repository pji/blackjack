"""
test_game.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.game module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from functools import partial
import unittest

from blackjack import cards, game, players


class GameTestCase(unittest.TestCase):
    def test_deal(self):
        """Given a deck and a dealer, deal() should deal an initial 
        hand of blackjack to the dealer from the deck.
        """
        expected_cls = cards.Hand
        expected_hand_len = 2
        expected_dealer_facing = [cards.UP, cards.DOWN,]
        expected_deck_size = 310
        
        deck = cards.Deck.build(6)
        d = players.Player()
        game.deal(deck, d)
        actual_hand_len = len(d.hands[0])
        actual_dealer_facing = [card.facing for card in d.hands[0]]
        actual_deck_size = len(deck)
        
        self.assertTrue(isinstance(d.hands[0], expected_cls))
        self.assertEqual(expected_hand_len, actual_hand_len)
        self.assertEqual(expected_dealer_facing, actual_dealer_facing)
        self.assertEqual(expected_deck_size, actual_deck_size)
    
    def test_play_bust(self):
        """Given a deck and a dealer with a dealt hand, play() should 
        deal cards to the dealer until the dealer stands on a bust.
        """
        expected = [
            cards.Card(2, 1),
            cards.Card(3, 2),
            cards.Card(6, 0),
            cards.Card(5, 1), 
            cards.Card(11, 3),
        ]
        
        h = cards.Hand([
            expected[0],
            expected[1],
        ])
        deck = cards.Deck([
            expected[4],
            expected[3],
            expected[2],
        ])
        d = players.Player((h,))
        d.will_hit = partial(players.dealer_will_hit, None)
        game.play(deck, d)
        actual = d.hands[0].cards
        
        self.assertEqual(expected, actual)
    
    def test_play_17_plus(self):
        """Given a deck and a dealer with a dealt hand, play() should 
        deal cards to the dealer until the dealer stands on a score of 
        17 or more.
        """
        expected = [
            cards.Card(10, 1),
            cards.Card(3, 2),
            cards.Card(7, 0),
        ]
        
        h = cards.Hand([
            expected[0],
            expected[1],
        ])
        deck = cards.Deck([
            expected[2],
        ])
        d = players.Player((h,))
        d.will_hit = partial(players.dealer_will_hit, None)
        game.play(deck, d)
        actual = d.hands[0].cards
        
        self.assertEqual(expected, actual)
        