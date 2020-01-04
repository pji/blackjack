"""
test_game.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.game module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from copy import deepcopy
from functools import partial
import inspect
from itertools import zip_longest
import unittest as ut
from unittest.mock import Mock, call

from blackjack import cards, game, players


class GameTestCase(ut.TestCase):
    def test_exists(self):
        """The class Game should exist in the game module."""
        names = [item[0] for item in inspect.getmembers(game)]
        self.assertTrue('Game' in names)
    
    # Game.__init__() tests.
    def test_deck_given(self):
        """If a deck is given, it should be stored in the deck 
        attribute.
        """
        expected = cards.Deck.build()
        
        g = game.Game(expected)
        actual = g.deck
        
        self.assertTrue(expected is actual)
    
    def test_deck_default(self):
        """If no deck is given, a casino deck should be created and 
        stored in the deck attribute.
        """
        expected_cls = cards.Deck
        expected_len = 52 * 6
        
        g = game.Game()
        actual_cls = g.deck
        actual_len = len(g.deck)
        
        self.assertTrue(isinstance(actual_cls, expected_cls))
        self.assertEqual(expected_len, actual_len)
    
    def test_dealer_default(self):
        """If not passed a dealer, the game should create a dealer."""
        expected = players.Dealer
        
        g = game.Game()
        actual = g.dealer
        
        self.assertTrue(isinstance(actual, expected))
    
    def test_dealer_given(self):
        """If given a dealer, the game should use it."""
        expected = 'Eric'
        
        dealer = players.Dealer(name=expected)
        g = game.Game(dealer=dealer)
        actual = g.dealer.name
        
        self.assertEqual(expected, actual)
    
    def test_ui_default(self):
        """If no UI is given, the game should create a BaseUI 
        object.
        """
        expected = game.BaseUI
        
        g = game.Game()
        actual = g.ui
        
        self.assertTrue(isinstance(actual, expected))
    
    def test_ui_given(self):
        """If a UI is given, the game should use it."""
        class Spam(game.BaseUI):
            pass
        expected = Spam
        
        g = game.Game(ui=Spam())
        actual = g.ui
        
        self.assertTrue(isinstance(actual, expected))
    
    def test_playerlist_default(self):
        """If not given players, the playerlist attribute should be 
        initialized to an empty tuple.
        """
        expected = ()
        
        g = game.Game()
        actual = g.playerlist
        
        self.assertEqual(expected, actual)
    
    def test_playerlist_given(self):
        """If given a list of players, that list should be stored in 
        the playerlist attribute.
        """
        expecteds = (
            players.Player(name='John'),
            players.Player(name='Michael'),
            players.Player(name='Graham'),
        )
        
        g = game.Game(playerlist=expecteds)
        actuals = g.playerlist
        
        for expected, actual in zip_longest(expecteds, actuals):
            self.assertTrue(expected is actual)
    
    # Game.deal() tests.
    def test_deal(self):
        """In a Game object with a deck and a dealer, deal() should 
        deal an initial hand of blackjack to the dealer from the 
        deck.
        """
        expected_cls = cards.Hand
        expected_hand_len = 2
        expected_dealer_facing = [cards.UP, cards.DOWN,]
        expected_deck_size = 310
        
        g = game.Game()
        g.deal()
        actual_hand_len = len(g.dealer.hands[0])
        actual_dealer_facing = [card.facing for card in g.dealer.hands[0]]
        actual_deck_size = len(g.deck)
        
        self.assertTrue(isinstance(g.dealer.hands[0], expected_cls))
        self.assertEqual(expected_hand_len, actual_hand_len)
        self.assertEqual(expected_dealer_facing, actual_dealer_facing)
        self.assertEqual(expected_deck_size, actual_deck_size)
    
    def test_deal_with_ui(self):
        """In a Game object with a deck and dealer,  deal() should 
        deal an initial hand of blackjack to the dealer from the deck 
        and update the UI.
        """
        cardlist = cards.Deck([
            cards.Card(11, 0),
            cards.Card(11, 3),
        ])
        hand = cards.Hand()
        hand.cards = cardlist[::-1]
        dealer = players.Player()
        expected = ['deal', dealer, hand]
        
        ui = Mock()
        deck = cards.Deck(cardlist)
        g = game.Game(dealer=dealer, ui=ui)
        g.deck = deck
        g.deal()
        
        ui.update.assert_called_with(*expected)
    
    def test_deal_with_players(self):
        """In a Game object with a deck, dealer, and player in the 
        playerlist, deal() should deal an initial hand of blackjack 
        to the dealer and the player from the deck.
        """
        expected_cls = cards.Hand
        expected_hand_len = 2
        expected_dealer_facing = [cards.UP, cards.DOWN,]
        expected_player_facing = [cards.UP, cards.UP,]
        expected_deck_size = 308
        
        deck = cards.Deck.build(6)
        dealer = players.Dealer(name='Dealer')
        player = players.Dealer(name='Player')
        g = game.Game(deck, dealer, (player,))
        g.deal()
        
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
    
    # Game.play() tests.
    def test_play_bust(self):
        """In a Game object with a deck and a dealer with a dealt 
        hand, play() should deal cards to the dealer until the dealer 
        stands on a bust.
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
        g = game.Game()
        g.deck = deck
        g.dealer.hands = (h,)
        g.play()
        actual = g.dealer.hands[0].cards
        
        self.assertEqual(expected, actual)
    
    def test_play_dealer_17_plus(self):
        """In a Game object with a deck and a dealer, play() should 
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
        g = game.Game()
        g.deck = deck
        g.dealer.hands = [h,]
        g.play()
        actual = g.dealer.hands[0].cards
        
        self.assertEqual(expected, actual)

    def test_play_with_players(self):
        """In a Game with a deck, dealer with a hand, and a player 
        with a hand, play a round of blackjack.
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
        g = game.Game(deck, dealer, (player,))
        g.play()
        actual_dhand = dealer.hands[0]
        actual_phand = player.hands[0]
        
        self.assertEqual(expected_dhand, actual_dhand)
        self.assertEqual(expected_phand, actual_phand)
    
    def test_play_with_ui(self):
        """Given a deck, dealer, and UI, play() should deal cards to 
        the dealer until the dealer stands on a score of 17 or more 
        and update the UI.
        """
        dealer = players.Dealer(name='Dealer')
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
        ui = Mock()
        g = game.Game(dealer=dealer, ui=ui)
        g.deck = deck
        g.play()
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)
