"""
test_game.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.game module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from functools import partial
import unittest
from unittest.mock import Mock, call

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
    
    def test_deal_with_ui(self):
        """Given a deck, dealer, and UI, deal() should deal an initial 
        hand of blackjack to the dealer from the deck and update the 
        UI.
        """
        cardlist = cards.Deck([
            cards.Card(11, 0),
            cards.Card(11, 3),
        ])
        hand = cards.Hand()
        hand.cards = cardlist[::-1]
        dealer = players.Player()
        expected = ['deal', dealer, hand]
        
        deck = cards.Deck(cardlist)
        ui = Mock()
        game.deal(deck, dealer, ui=ui)
        
        ui.update.assert_called_with(*expected)
    
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
    
    def test_play_with_ui(self):
        """Given a deck, dealer, and UI, play() should deal cards to 
        the dealer until the dealer stands on a score of 17 or more 
        and update the UI.
        """
        dealer = players.Player(name='Dealer')
        cardlist = [
            cards.Card(7, 0, cards.UP),
            cards.Card(6, 0, cards.UP),
            cards.Card(5, 0, cards.UP),
        ]
        expected_hand = cards.Hand(cardlist)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [
            call.update('flip', dealer, expected_hand),
            call.update('hit', dealer, expected_hand),
            call.update('stand', dealer, expected_hand),
        ]
        
        h = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(6, 0, cards.DOWN),
        ])
        deck = cards.Deck([
            cards.Card(5, 0, cards.DOWN),
        ])
        dealer.hands = ((h,))
        dealer.will_hit = partial(players.dealer_will_hit, None)
        ui = Mock()
        game.play(deck, dealer, ui=ui)
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)