"""
test_game.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.game module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from copy import deepcopy
from functools import partial
import unittest
from unittest.mock import Mock, call

from blackjack import cards, game, players


class GameTestCase(unittest.TestCase):
    # Test deal()
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
    
    def test_deal_with_players(self):
        """Given a deck, a dealer, and a player, deal() should deal an 
        initial hand of blackjack to the dealer and the player from 
        the deck.
        """
        expected_cls = cards.Hand
        expected_hand_len = 2
        expected_dealer_facing = [cards.UP, cards.DOWN,]
        expected_player_facing = [cards.UP, cards.UP,]
        expected_deck_size = 308
        
        deck = cards.Deck.build(6)
        dealer = players.Dealer(name='Dealer')
        player = players.Dealer(name='Player')
        game.deal(deck, dealer, (player,))
        
        # Dealer
        actual_hand_len_d = len(dealer.hands[0])
        actual_dealer_facing = [card.facing for card in dealer.hands[0]]
        
        self.assertTrue(isinstance(dealer.hands[0], expected_cls))
        self.assertEqual(expected_hand_len, actual_hand_len_d)
        self.assertEqual(expected_dealer_facing, actual_dealer_facing)
        
        # Player
        actual_hand_len_p = len(player.hands[0])
        actual_player_facing = [card.facing for card in player.hands[0]]
        
        self.assertTrue(isinstance(player.hands[0], expected_cls))
        self.assertEqual(expected_hand_len, actual_hand_len_p)
        self.assertEqual(expected_player_facing, actual_player_facing)
        
        # Deck
        actual_deck_size = len(deck)
        
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
    
    # Test play().
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
    
    def test_play_with_players(self):
        """Given a deck, dealer with a hand, and a player with a hand, 
        play a round of blackjack.
        """
        expected_dhand = cards.Hand([
            cards.Card(5, 0),
            cards.Card(5, 1),
            cards.Card(11, 0),
        ])
        expected_phand = cards.Hand([
            cards.Card(5, 2),
            cards.Card(5, 3),
            cards.Card(11, 3),            
        ])
        
        deck = cards.Deck([
            cards.Card(11, 0, cards.DOWN),
            cards.Card(11, 3, cards.DOWN),
        ])
        dealer = players.Dealer('Dealer')
        dealer.hands = [cards.Hand([
            cards.Card(5, 0),
            cards.Card(5, 1),
        ]),]
        player = players.Dealer('Player')
        player.hands = [cards.Hand([
            cards.Card(5, 2),
            cards.Card(5, 3),
        ]),]
        game.play(deck, dealer, (player,))
        actual_dhand = dealer.hands[0]
        actual_phand = player.hands[0]
        
        self.assertEqual(expected_dhand, actual_dhand)
        self.assertEqual(expected_phand, actual_phand)
    
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
    
    # Test split().
    def test_split_no_splits(self):
        """Given a player and a hand, split should determine if the 
        player's hand can be split. If not, it should exit.
        """
        expected_h1 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(2, 1),
        ])
        expected_len = 1
        
        p1 = players.Player((deepcopy(expected_h1),), 'Player1')
        game.split(p1, p1.hands[0])
        actual_h1 = p1.hands[0]
        actual_len1 = len(p1.hands)
        
        self.assertEqual(expected_h1, actual_h1)
        self.assertEqual(expected_len, actual_len1)