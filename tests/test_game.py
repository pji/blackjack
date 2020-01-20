"""
test_game.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.game module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from copy import copy, deepcopy
from functools import partial
import inspect
from itertools import zip_longest
import unittest as ut
from unittest.mock import Mock, call, patch

from blackjack import cards, game, players


class EngineTestCase(ut.TestCase):
    def test_exists(self):
        """The class Game should exist in the game module."""
        names = [item[0] for item in inspect.getmembers(game)]
        self.assertTrue('Engine' in names)
    
    
    # Engine.__init__() tests.
    def test_deck_given(self):
        """If a deck is given, it should be stored in the deck 
        attribute.
        """
        expected = cards.Deck.build()
        
        g = game.Engine(expected)
        actual = g.deck
        
        self.assertTrue(expected is actual)
    
    def test_deck_default(self):
        """If no deck is given, a casino deck should be created and 
        stored in the deck attribute.
        """
        expected_cls = cards.Deck
        expected_len = 52 * 6
        
        g = game.Engine()
        actual_cls = g.deck
        actual_len = len(g.deck)
        
        self.assertTrue(isinstance(actual_cls, expected_cls))
        self.assertEqual(expected_len, actual_len)
    
    def test_dealer_default(self):
        """If not passed a dealer, the game should create a dealer."""
        expected = players.Dealer
        
        g = game.Engine()
        actual = g.dealer
        
        self.assertTrue(isinstance(actual, expected))
    
    def test_dealer_given(self):
        """If given a dealer, the game should use it."""
        expected = 'Eric'
        
        dealer = players.Dealer(name=expected)
        g = game.Engine(dealer=dealer)
        actual = g.dealer.name
        
        self.assertEqual(expected, actual)
    
    def test_ui_default(self):
        """If no UI is given, the game should create a _BaseUI 
        object.
        """
        expected = game._BaseUI
        
        g = game.Engine()
        actual = g.ui
        
        self.assertTrue(isinstance(actual, expected))
    
    def test_ui_given(self):
        """If a UI is given, the game should use it."""
        class Spam(game.BaseUI):
            pass
        expected = Spam
        
        g = game.Engine(ui=Spam())
        actual = g.ui
        
        self.assertTrue(isinstance(actual, expected))
    
    def test_playerlist_default(self):
        """If not given players, the playerlist attribute should be 
        initialized to an empty tuple.
        """
        expected = ()
        
        g = game.Engine()
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
        
        g = game.Engine(playerlist=expecteds)
        actuals = g.playerlist
        
        for expected, actual in zip_longest(expecteds, actuals):
            self.assertTrue(expected is actual)
    
    def test_buyin_given(self):
        """If given a value for buyin, that value should be stored in 
        the buyin attribute.
        """
        expected = 500.00
        
        g = game.Engine(buyin=expected)
        actual = g.buyin
        
        self.assertEqual(expected, actual)
    
    def test_buyin_default(self):
        """If no value is given for buyin, the value of the buyin 
        attribute should default to zero.
        """
        expected = 0
        
        g = game.Engine()
        actual = g.buyin
        
        self.assertEqual(expected, actual)
    
    def test_seats(self):
        """On initiation of a Engine object, the value of the seats 
        attribute should be the length of the playerlist. This will 
        be used as the maximum number of players that can join the 
        game.
        """
        expected = 3
        
        playerlist = [
            players.Player(),
            players.Player(),
            players.Player(),
        ]
        g = game.Engine(playerlist=playerlist)
        actual = g.seats
        
        self.assertEqual(expected, actual)
    
    
    # Test Engine.new_game().
    def test_players_join(self):
        """When players join a game, it should send a join 
        event to the UI for each player in the game.
        """
        ui = Mock()
        playerlist = [
            players.Player(),
            players.Player(),
            players.Player(),
        ]
        e = game.Engine(playerlist=playerlist, ui=ui)
        expected = [
            call.joins(e.dealer),
            call.joins(playerlist[0]),
            call.joins(playerlist[1]),
            call.joins(playerlist[2]),
        ]
        
        e.new_game()
        actual = ui.mock_calls
        
        self.assertListEqual(expected, actual)
    
    
    # Engine.deal() tests.
    def test_deal(self):
        """In a Engine object with a deck and a dealer, deal() should 
        deal an initial hand of blackjack to the dealer from the 
        deck.
        """
        expected_cls = cards.Hand
        expected_hand_len = 2
        expected_dealer_facing = [cards.UP, cards.DOWN,]
        expected_deck_size = 310
        
        g = game.Engine()
        g.deal()
        actual_hand_len = len(g.dealer.hands[0])
        actual_dealer_facing = [card.facing for card in g.dealer.hands[0]]
        actual_deck_size = len(g.deck)
        
        self.assertTrue(isinstance(g.dealer.hands[0], expected_cls))
        self.assertEqual(expected_hand_len, actual_hand_len)
        self.assertEqual(expected_dealer_facing, actual_dealer_facing)
        self.assertEqual(expected_deck_size, actual_deck_size)
    
    def test_deal_with_ui(self):
        """In a Engine object with a deck and dealer,  deal() should 
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
        expected = [dealer, hand]
        
        ui = Mock()
        deck = cards.Deck(cardlist)
        g = game.Engine(dealer=dealer, ui=ui)
        g.deck = deck
        g.deal()
        
        ui.deal.assert_called_with(*expected)
    
    def test_deal_with_players(self):
        """In a Engine object with a deck, dealer, and player in the 
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
        g = game.Engine(deck, dealer, (player,))
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
    
    
    # Engine.play() tests.
    def test_play_bust(self):
        """In a Engine object with a deck and a dealer with a dealt 
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
        g = game.Engine()
        g.deck = deck
        g.dealer.hands = (h,)
        g.play()
        actual = g.dealer.hands[0].cards
        
        self.assertEqual(expected, actual)
    
    def test_play_dealer_17_plus(self):
        """In a Engine object with a deck and a dealer, play() should 
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
        g = game.Engine()
        g.deck = deck
        g.dealer.hands = [h,]
        g.play()
        actual = g.dealer.hands[0].cards
        
        self.assertEqual(expected, actual)

    def test_play_with_players(self):
        """In a Engine with a deck, dealer with a hand, and a player 
        with a hand, play a round of blackjack.
        """
        expected_dhand = cards.Hand([
            cards.Card(5, 0),
            cards.Card(5, 1),
            cards.Card(11, 0),
        ])
        expected_phand = cards.Hand([
            cards.Card(5, 2),
            cards.Card(4, 3),
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
        player = players.AutoPlayer('Player')
        player.hands = [cards.Hand([
            cards.Card(5, 2),
            cards.Card(4, 3),
        ]),]
        g = game.Engine(deck, dealer, (player,))
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
        # between the first two calls since the cards in the hand will 
        # be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.hit(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [
            call.flip(dealer, expected_hand),
            call.hit(dealer, expected_hand),
            call.stand(dealer, expected_hand),
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
        g = game.Engine(dealer=dealer, ui=ui)
        g.deck = deck
        g.play()
        actual = ui.mock_calls
        
        self.assertListEqual(expected, actual)
    
    def test_play_with_split(self):
        """If given a hand that can be split and a player who will 
        split that hand, play() should handle both of the hands.
        """
        exp_h1 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(2, 2),
            cards.Card(9, 3),
        ])
        exp_h2 = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 3),
        ])
        expected = (exp_h1, exp_h2)
        
        hand = cards.Hand([
            exp_h1[0],
            exp_h2[0],
        ])
        dhand = cards.Hand([
            cards.Card(10, 0),
            cards.Card(10, 1),
        ])
        player = players.AutoPlayer((hand,), name='Terry')
        dealer = players.Dealer((dhand,))
        deck = cards.Deck([
            cards.Card(1, 3, cards.DOWN),
            cards.Card(9, 3, cards.DOWN),
            cards.Card(2, 2, cards.DOWN),
        ])
        g = game.Engine(deck, dealer, (player,))
        g.play()
        actual = player.hands
        
        self.assertEqual(expected, actual)
    
    def test_play_with_ace_split(self):
        """Given a hand with two aces and a player who will split that 
        hand, play() should split the hand and hit each of the split 
        hands only once before standing.
        """
        exp_h1 = cards.Hand([
            cards.Card(1, 0),
            cards.Card(2, 2),
        ])
        exp_h2 = cards.Hand([
            cards.Card(1, 3),
            cards.Card(1, 3),
        ])
        expected = (exp_h1, exp_h2)
        
        hand = cards.Hand([
            exp_h1[0],
            exp_h2[0],
        ])
        dhand = cards.Hand([
            cards.Card(10, 0),
            cards.Card(10, 1),
        ])
        player = players.AutoPlayer((hand,), name='Terry')
        dealer = players.Dealer((dhand,))
        deck = cards.Deck([
            exp_h2[1],
            exp_h1[1],
        ])
        for card in deck:
            card.flip()
        g = game.Engine(deck, dealer, (player,))
        g.play()
        actual = player.hands
        
        self.assertEqual(expected, actual)
    
    def test_play_with_double_down(self):
        """Given a hand with a value from 9 to 11 and a player who 
        will double down, play() should hit the hand once and stand.
        """
        expected_hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
            cards.Card(11, 0),
        ])
        expected_dd = True
        
        hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        deck = cards.Deck([
            cards.Card(11, 0, cards.DOWN),
        ])
        dhand = cards.Hand([
            cards.Card(10, 0),
            cards.Card(7, 1),
        ])
        dealer = players.Dealer([dhand,], 'Dealer')
        g = game.Engine(deck, dealer, (player,), None, 20)
        g.play()
        actual_hand = player.hands[0]
        actual_dd = player.hands[0].doubled_down
        
        self.assertEqual(expected_hand, actual_hand)
        self.assertEqual(expected_dd, actual_dd)
    
    def test_play_with_double_down(self):
        """Given a dealer hand with an ace showing an a player who 
        will insure, play() should insure the player then play the 
        round as usual.
        """
        expected_hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
            cards.Card(11, 0),
        ])
        expected_insured = 10
        
        hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        deck = cards.Deck([
            cards.Card(8, 1, cards.DOWN),
            cards.Card(11, 0, cards.DOWN),
        ])
        dhand = cards.Hand([
            cards.Card(1, 0),
            cards.Card(7, 1, cards.DOWN),
        ])
        dealer = players.Dealer([dhand,], 'Dealer')
        g = game.Engine(deck, dealer, (player,), None, 20)
        g.play()
        actual_hand = player.hands[0]
        actual_insured = player.insured
        
        self.assertEqual(expected_hand, actual_hand)
        self.assertEqual(expected_insured, actual_insured)        
    
    
    # Test Engine.end().
    def test_end_player_wins(self):
        """If the player wins, the player gets double their initial 
        bet.
        """
        expected = 40
        
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    def test_end_player_loses(self):
        """If the player loses, the player loses their initial bet."""
        expected = 0
        
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(9, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    def test_end_tie_with_ui(self):
        """If the player ties, the player gets back their initial 
        bet.
        """
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        expected = 20
        expected_call = call.tie(player, 20)
        
        dhand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Engine(None, dealer, (player,), ui, 20)
        g.end()
        actual = player.chips
        actual_call = ui.mock_calls[-1]
        
        self.assertEqual(expected, actual)
        self.assertEqual(expected_call, actual_call)
    
    def test_end_player_blackjack(self):
        """If the player wins with a blackjack, they get two and a 
        half times their initial bet back.
        """
        expected = 50
        
        phand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(12, 1),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(13, 0),
            cards.Card(12, 3),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    def test_end_player_split_not_blackjack(self):
        """If the hand was split from aces it cannot be counted as 
        a blackjack.
        """
        expected = 40
        
        hand1 = cards.Hand([
            cards.Card(1, 1),
            cards.Card(10, 0),
        ])
        hand2 = cards.Hand([
            cards.Card(1, 2),
            cards.Card(2, 0),
            cards.Card(9, 1),
        ])
        player = players.Player([hand1, hand2], 'Michael', 0)
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    def test_end_with_ui_won(self):
        """Once the payout is determined, end() should send the event 
        to the UI.
        """
        cardlist = [
            cards.Card(7, 0, cards.UP),
            cards.Card(6, 0, cards.UP),
            cards.Card(5, 0, cards.UP),
        ]
        phand = cards.Hand(cardlist)
        player = players.AutoPlayer((phand,), 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.wins(player, 40),]
        
        dhand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Engine(None, dealer, (player,), ui, 20)
        g.end()
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)
    
    def test_end_with_ui_loses(self):
        """Once the loss is determined, end() should send the event 
        to the UI.
        """
        cardlist = [
            cards.Card(7, 0, cards.UP),
            cards.Card(6, 0, cards.UP),
            cards.Card(10, 0, cards.UP),
        ]
        phand = cards.Hand(cardlist)
        player = players.AutoPlayer((phand,), 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.loses(player)]
        
        dhand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Engine(None, dealer, (player,), ui, 20)
        g.end()
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)
    
    def test_end_split_with_ui(self):
        """Once the payout is determined, end() should send the event 
        to the UI. If the hand is split, that event should be 
        'splitpayout' if the hand wins.
        """
        hand2 = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        hand1 = cards.Hand([
            cards.Card(1, 2),
            cards.Card(2, 0),
            cards.Card(9, 1),
        ])
        player = players.Player([hand1, hand2], 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.wins_split(player, 40),]
        
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Engine(None, dealer, (player,), ui, 20)
        g.end()
        actual = [ui.mock_calls[-1],]
        
        self.assertEqual(expected, actual)
    
    def test_end_split_with_loss_ui(self):
        """Once the payout is determined, end() should send the event 
        to the UI. If the hand is split, that event should be 
        'splitlost' if the hand loses.
        """
        hand2 = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        hand1 = cards.Hand([
            cards.Card(1, 2),
            cards.Card(2, 0),
            cards.Card(9, 1),
        ])
        player = players.Player([hand2, hand1], 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.loses_split(player),]
        
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Engine(None, dealer, (player,), ui, 20)
        g.end()
        actual = [ui.mock_calls[-1],]
        
        self.assertEqual(expected, actual)
    
    def test_end_split_with_tie_ui(self):
        """Once the payout is determined, end() should send the event 
        to the UI. If the hand is split, that event should be 
        'splitlost' if the hand loses.
        """
        hand2 = cards.Hand([
            cards.Card(7, 1),
            cards.Card(10, 0),
        ])
        hand1 = cards.Hand([
            cards.Card(1, 2),
            cards.Card(2, 0),
            cards.Card(9, 1),
        ])
        player = players.Player([hand1, hand2], 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.ties_split(player, 20),]
        
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Engine(None, dealer, (player,), ui, 20)
        g.end()
        actual = [ui.mock_calls[-1],]
        
        self.assertEqual(expected, actual)
    
    def test_end_split_blackjack_with_ui(self):
        """Once the payout is determined, end() should send the event 
        to the UI. If the hand is split and it's a blackjack, the 
        event should be 'splitpayout'.
        """
        hand2 = cards.Hand([
            cards.Card(1, 1),
            cards.Card(10, 0),
        ])
        hand1 = cards.Hand([
            cards.Card(1, 2),
            cards.Card(2, 0),
            cards.Card(9, 1),
        ])
        player = players.Player([hand1, hand2], 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.wins_split(player, 40),]
        
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Engine(None, dealer, (player,), ui, 20)
        g.end()
        actual = [ui.mock_calls[-1],]
        
        self.assertEqual(expected, actual)
    
    def test_end_with_double_down(self):
        """If the hand was doubled down, the pay out should quadruple 
        the initial bet.
        """
        expected = 80
        
        phand = cards.Hand([
            cards.Card(4, 1),
            cards.Card(6, 2),
            cards.Card(10, 0),
        ])
        phand.doubled_down = True
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    def test_end_with_insured(self):
        """If the player was insured and the dealer had a blackjack, 
        the insurance pay out should double the insurance amount.
        """
        phand = cards.Hand([
            cards.Card(4, 1),
            cards.Card(6, 2),
            cards.Card(10, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        expected = [call.insurepay(player, 20),]
        
        player.insured = 10
        dhand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Engine(None, dealer, (player,), ui, 20)
        g.end()
        actual = [ui.mock_calls[-2],]
        
        self.assertEqual(expected, actual)
    
    def test_end_dealer_blackjack_player_21(self):
        """Given a dealer hand that is a blackjack, all players who 
        don't have blackjack lose.
        """
        expected = 0
        
        phand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(10, 0),
            cards.Card(9, 1),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    
    # Engine._split() tests.
    def test__split_cannot_split(self):
        """Given a hand and a player, if the hand cannot be split, 
        _split() should not split it and return false.
        """
        expected_h1 = [cards.Hand([
            cards.Card(11, 3),
            cards.Card(2, 1),
        ]),]
        expected_return = False
        
        p1 = players.AutoPlayer(copy(expected_h1), name='John')
        playerlist = [p1,]
        g = game.Engine(None, None, playerlist)
        actual_return = g._split(expected_h1[0], p1)
        actual_h1 = p1.hands
        
        self.assertEqual(expected_h1, actual_h1)
        self.assertEqual(expected_return, actual_return)
    
    def test__split_does_split(self):
        """Given a hand and a player, if the hand can be split and the 
        player says to split, the hand should be split, and the method 
        should return True.
        """
        expected_hands = (
            cards.Hand([cards.Card(11, 3),]),
            cards.Hand([cards.Card(11, 1),]),
        )
        expected_return = True
        exp_chips = 0
        
        h1 = [cards.Hand([
            cards.Card(11, 3),
            cards.Card(11, 1),
        ]),]
        p1 = players.AutoPlayer(copy(h1), 'John', 20)
        playerlist = [p1,]
        g = game.Engine(None, None, playerlist, None, 20)
        actual_return = g._split(h1[0], p1)
        actual_hands = p1.hands
        act_chips = p1.chips
        
        self.assertEqual(expected_hands, actual_hands)
        self.assertEqual(expected_return, actual_return)
        self.assertEqual(exp_chips, act_chips)
    
    def test__split_with_ui(self):
        """If _split() splits the hand, it should send the event, 
        the player, and the new hand to the UI.
        """
        hands = (
            cards.Hand([cards.Card(11, 3),]),
            cards.Hand([cards.Card(11, 1),]),
        )
        h1 = [cards.Hand([
            cards.Card(11, 3),
            cards.Card(11, 1),
        ]),]
        p1 = players.AutoPlayer(copy(h1), 'John', 200)
        expected = (p1, 20)
        
        playerlist = [p1,]
        g = game.Engine(None, None, playerlist, Mock(), 20)
        _ = g._split(h1[0], p1)

        g.ui.splits.assert_called_with(*expected)
    
    
    # Test Engine._ace_split_hit()
    def test__ace_split_hit(self):
        """Given a hand with an ace that had been split, 
        _ace_split_hit() should give hand one hit and then 
        stand.
        """
        expected = cards.Hand([
            cards.Card(1, 3),
            cards.Card(11, 0, cards.DOWN),
        ])
        
        deck = cards.Deck([
            expected[1],
        ])
        hand = cards.Hand([
            expected[0],
        ])
        player = players.AutoPlayer((hand,), name='Eric')
        g = game.Engine(deck, None, (player,))
        g._ace_split_hit(player, hand)
        actual = player.hands[0]
        
        self.assertEqual(expected, actual)
    
    def test__ace_split_hit_ui(self):
        """Given a hand with an ace that had been split, 
        _ace_split_hit() should send an event to the UI 
        for the single hit and the stand.
        """
        hand = cards.Hand([
            cards.Card(1, 3),
        ])
        player = players.AutoPlayer([hand,], name='John')
        expected = [
            call.hit(player, hand),
            call.stand(player, hand),
        ]
        
        deck = cards.Deck([
            cards.Card(11, 0, cards.DOWN),
        ])
        ui = Mock()
        g = game.Engine(deck, None, (player,), ui)
        g._ace_split_hit(player, hand)
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)
    
    
    # Test Engine.start().
    def test_start_take_payment(self):
        """In a Engine with players who will buy-in and a buy-in, 
        buyin() should take the buy-in from the player's chips 
        totals.
        """
        expected = 180.00
        
        p1 = players.AutoPlayer([], 'John', 200)
        p2 = players.AutoPlayer([], 'Michael', 200)
        playerlist = [p1, p2]
        g = game.Engine(None, None, playerlist, None, 20.00)
        g.start()
        actual_p1 = p1.chips
        actual_p2 = p2.chips
        
        self.assertEqual(expected, actual_p1)
        self.assertEqual(expected, actual_p2)
    
    def test_start_too_few_chips(self):
        """If a player tries to buy into a game but does not have 
        enough chips, start() should remove them from the game and 
        add a new player.
        """
        expected = players.Player
        
        p1 = players.Player(name='John', chips = 1)
        g = game.Engine(None, None, [p1,], None, 20)
        g.start()
        actual = g.playerlist[0]
        
        self.assertTrue(isinstance(actual, expected))
        self.assertNotEqual(expected, actual)
    
    def test_start_buyin_ui(self):
        """When a player buys into the round, start() should send that 
        event to the UI.
        """
        buyin = 20.00
        chips = 200
        p1 = players.AutoPlayer([], 'John', chips)
        p2 = players.AutoPlayer([], 'Michael', chips)
        expected = [
            call.bet(p1, buyin),
            call.bet(p2, buyin),
        ]
        
        playerlist = [p1, p2]
        ui = Mock()
        g = game.Engine(None, None, playerlist, ui, buyin)
        g.start()
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)        
    
    @patch('blackjack.game.make_player')
    def test_start_remove_ui(self, mock_make_player):
        """When a player is removed, start() should send that event to 
        the UI and then send an event for the addition of the new 
        player.
        """
        unexp_player = players.AutoPlayer([], 'Eric', 1)
        exp_player = players.AutoPlayer([], 'Spam', 1)
        exp_calls = [
            call.leaves(unexp_player),
            call.joins(exp_player),
        ]
        
        ui = Mock()
        mock_make_player.return_value = exp_player
        g = game.Engine(playerlist=(unexp_player,), ui=ui, buyin=20)
        g.start()
        act_player = g.playerlist[0]
        act_calls = ui.mock_calls
        
        self.assertEqual(exp_player, act_player)
        self.assertEqual(exp_calls, act_calls)
    
    
    # Test Engine._remove_player().
    def test__remove_player(self):
        """Given player, _remove_player() should remove that player 
        from the playlist attribute.
        """
        expected = [None,]
        
        p1 = players.Player(name='John', chips = 1)
        g = game.Engine(None, None, [p1,], None, 20)
        g._remove_player(p1)
        actual = g.playerlist
        
        self.assertEqual(expected, actual)
    
    
    # Test Engine._compare_score().
    def test__compare_score_player_win(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return True if the player's score is higher.
        """
        expected = True
        
        p_hand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(11, 3),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(7, 2),
        ])
        g = game.Engine()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
    
    def test__compare_score_player_lose(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return False if the player's score is lower.
        """
        expected = False
        
        p_hand = cards.Hand([
            cards.Card(3, 1),
            cards.Card(11, 3),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(7, 2),
        ])
        g = game.Engine()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
        
    def test__compare_score_player_bust(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return False if the player busts.
        """
        expected = False
        
        p_hand = cards.Hand([
            cards.Card(3, 1),
            cards.Card(11, 3),
            cards.Card(12, 2),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(7, 2),
        ])
        g = game.Engine()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
        
    def test__compare_score_dealer_bust(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return True if the dealer busts.
        """
        expected = True
        
        p_hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(12, 2),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(6, 1),
            cards.Card(7, 2),
        ])
        g = game.Engine()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
        
    def test__compare_score_tie(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return None if it is a tie.
        """
        expected = None
        
        p_hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(12, 2),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(5, 1),
            cards.Card(5, 2),
        ])
        g = game.Engine()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
        
    def test__compare_score_dealer_wins_busts(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return True if the dealer busts.
        """
        expected = False
        
        p_hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(12, 2),
            cards.Card(13, 0),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(6, 1),
            cards.Card(7, 2),
        ])
        g = game.Engine()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
    
    
    # Test Engine._double_down().
    def test__double_down(self):
        """Given a hand and a player who will double down and can 
        double down, _double_down() should set the doubled_down 
        attribute on the hand and take the player's additional bet.
        """
        expected_dd = True
        expected_chips = 0
        
        hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        g = game.Engine(None, None, (player,), None, 20)
        g._double_down(player, hand)
        actual_dd = hand.doubled_down
        actual_chips = player.chips
        
        self.assertEqual(expected_dd, actual_dd)
        self.assertEqual(expected_chips, actual_chips)
    
    def test__double_down_ui(self):
        """If the player doubles down, _double_down() should send that 
        event to the UI.
        """
        hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        expected = (player, 20)

        ui = Mock()
        g = game.Engine(None, None, (player,), ui, 20)
        g._double_down(player, hand)
        
        ui.doubledown.assert_called_with(*expected)
    
    def test__double_down_not_on_blackjack(self):
        """If player has a blackjack, _double_down() should not allow 
        the hand to be doubled down.
        """
        expected_dd = False
        expected_chips = 20
        
        hand = cards.Hand([
            cards.Card(1, 2),
            cards.Card(13, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        g = game.Engine(None, None, (player,), None, 20)
        g._double_down(player, hand)
        actual_dd = hand.doubled_down
        actual_chips = player.chips
        
        self.assertEqual(expected_dd, actual_dd)
        self.assertEqual(expected_chips, actual_chips)
    
    
    # Test Engine._insure()
    def test__insure(self):
        """Given a dealer hand a player can ensure and a player who 
        will insure, _insure() should set the insured attribute on 
        the player and take the player's additional bet.
        """
        expected_insured = 10
        expected_chips = 0
        
        dhand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        player = players.AutoPlayer(cards.Hand(), 'Eric', 10)
        g = game.Engine(None, dealer, (player,), None, 20)
        g._insure(player)
        actual_insured = player.insured
        actual_chips = player.chips
        
        self.assertEqual(expected_insured, actual_insured)
        self.assertEqual(expected_chips, actual_chips)
    
    def test__insure_zero(self):
        """Given a dealer hand a player can ensure and a player who 
        will insure, _insure() should set the insured attribute on 
        the player and take the player's additional bet.
        """
        expected_insured = 0
        expected_chips = 10
        
        dhand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        player = players.BetterPlayer(cards.Hand(), 'Eric', 10)
        g = game.Engine(None, dealer, (player,), None, 20)
        g._insure(player)
        actual_insured = player.insured
        actual_chips = player.chips
        
        self.assertEqual(expected_insured, actual_insured)
        self.assertEqual(expected_chips, actual_chips)
    
    def test__insure_ui(self):
        """If the player insures, _insure() should send that 
        event to the UI.
        """
        dhand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        player = players.AutoPlayer(None, 'Eric', 20)
        expected = (player, 10)

        ui = Mock()
        g = game.Engine(None, dealer, (player,), ui, 20)
        g._insure(player)
        
        ui.insures.assert_called_with(*expected)
    
    
    # Test Engine._draw().
    def test__draw_deck_with_cards(self):
        """Draw a the top card from the game deck."""
        deck = cards.Deck.build(6)
        expected = deck[-1]
        
        g = game.Engine(deck)
        actual = g._draw()
        
        self.assertEqual(expected, actual)
    
    def test__draw_deck_with_no_cards(self):
        """If the game deck has no card, create, shuffle, and cut a 
        new deck, then draw.
        """
        expected = cards.Card
        
        g = game.Engine()
        g.deck = cards.Deck([])
        g.deck.size = 6
        actual = g._draw()
        
        self.assertTrue(isinstance(actual, expected))
    
    def test__draw_shuffled_ui(self):
        """If the deck is shuffled, _draw() should send that 
        event to the UI.
        """
        dhand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        ui = Mock()
        g = game.Engine(None, dealer, None, ui, 20)
        g.deck = cards.Deck([])
        g.deck.size = 6
        _ = g._draw()
        
        ui.shuffles.assert_called()
    
    
    # Test Engine._add_player().
    def test__add_player(self):
        """Given a player, _add_player() adds that player in the first 
        empty slot in the playerlist.
        """
        player = players.Player(name='Spam')
        expected = [player,]
        
        playerlist = [None,]
        g = game.Engine(None, None, playerlist, None, None)
        g._add_player(player)
        actual = g.playerlist
        
        self.assertEqual(expected, actual)


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
    
    def test_buyin_given(self):
        """If given a value for buyin, that value should be stored in 
        the buyin attribute.
        """
        expected = 500.00
        
        g = game.Game(buyin=expected)
        actual = g.buyin
        
        self.assertEqual(expected, actual)
    
    def test_buyin_default(self):
        """If no value is given for buyin, the value of the buyin 
        attribute should default to zero.
        """
        expected = 0
        
        g = game.Game()
        actual = g.buyin
        
        self.assertEqual(expected, actual)
    
    def test_seats(self):
        """On initiation of a Game object, the value of the seats 
        attribute should be the length of the playerlist. This will 
        be used as the maximum number of players that can join the 
        game.
        """
        expected = 3
        
        playerlist = [
            players.Player(),
            players.Player(),
            players.Player(),
        ]
        g = game.Game(playerlist=playerlist)
        actual = g.seats
        
        self.assertEqual(expected, actual)
    
    
    # Test Game.new_game().
    def test_players_join(self):
        """When players join a game, it should send a join 
        event to the UI for each player in the game.
        """
        ui = Mock()
        playerlist = [
            players.Player(),
            players.Player(),
            players.Player(),
        ]
        g = game.Game(playerlist=playerlist, ui=ui)
        expected = [
            call.update('join', g.dealer, ''),
            call.update('join', playerlist[0], ''),
            call.update('join', playerlist[1], ''),
            call.update('join', playerlist[2], ''),
        ]
        
        g.new_game()
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)
    
    
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
            cards.Card(4, 3),
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
        player = players.AutoPlayer('Player')
        player.hands = [cards.Hand([
            cards.Card(5, 2),
            cards.Card(4, 3),
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
    
    def test_play_with_split(self):
        """If given a hand that can be split and a player who will 
        split that hand, play() should handle both of the hands.
        """
        exp_h1 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(2, 2),
            cards.Card(9, 3),
        ])
        exp_h2 = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 3),
        ])
        expected = (exp_h1, exp_h2)
        
        hand = cards.Hand([
            exp_h1[0],
            exp_h2[0],
        ])
        dhand = cards.Hand([
            cards.Card(10, 0),
            cards.Card(10, 1),
        ])
        player = players.AutoPlayer((hand,), name='Terry')
        dealer = players.Dealer((dhand,))
        deck = cards.Deck([
            cards.Card(1, 3, cards.DOWN),
            cards.Card(9, 3, cards.DOWN),
            cards.Card(2, 2, cards.DOWN),
        ])
        g = game.Game(deck, dealer, (player,))
        g.play()
        actual = player.hands
        
        self.assertEqual(expected, actual)
    
    def test_play_with_ace_split(self):
        """Given a hand with two aces and a player who will split that 
        hand, play() should split the hand and hit each of the split 
        hands only once before standing.
        """
        exp_h1 = cards.Hand([
            cards.Card(1, 0),
            cards.Card(2, 2),
        ])
        exp_h2 = cards.Hand([
            cards.Card(1, 3),
            cards.Card(1, 3),
        ])
        expected = (exp_h1, exp_h2)
        
        hand = cards.Hand([
            exp_h1[0],
            exp_h2[0],
        ])
        dhand = cards.Hand([
            cards.Card(10, 0),
            cards.Card(10, 1),
        ])
        player = players.AutoPlayer((hand,), name='Terry')
        dealer = players.Dealer((dhand,))
        deck = cards.Deck([
            exp_h2[1],
            exp_h1[1],
        ])
        for card in deck:
            card.flip()
        g = game.Game(deck, dealer, (player,))
        g.play()
        actual = player.hands
        
        self.assertEqual(expected, actual)
    
    def test_play_with_double_down(self):
        """Given a hand with a value from 9 to 11 and a player who 
        will double down, play() should hit the hand once and stand.
        """
        expected_hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
            cards.Card(11, 0),
        ])
        expected_dd = True
        
        hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        deck = cards.Deck([
            cards.Card(11, 0, cards.DOWN),
        ])
        dhand = cards.Hand([
            cards.Card(10, 0),
            cards.Card(7, 1),
        ])
        dealer = players.Dealer([dhand,], 'Dealer')
        g = game.Game(deck, dealer, (player,), None, 20)
        g.play()
        actual_hand = player.hands[0]
        actual_dd = player.hands[0].doubled_down
        
        self.assertEqual(expected_hand, actual_hand)
        self.assertEqual(expected_dd, actual_dd)
    
    def test_play_with_double_down(self):
        """Given a dealer hand with an ace showing an a player who 
        will insure, play() should insure the player then play the 
        round as usual.
        """
        expected_hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
            cards.Card(11, 0),
        ])
        expected_insured = 10
        
        hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        deck = cards.Deck([
            cards.Card(8, 1, cards.DOWN),
            cards.Card(11, 0, cards.DOWN),
        ])
        dhand = cards.Hand([
            cards.Card(1, 0),
            cards.Card(7, 1, cards.DOWN),
        ])
        dealer = players.Dealer([dhand,], 'Dealer')
        g = game.Game(deck, dealer, (player,), None, 20)
        g.play()
        actual_hand = player.hands[0]
        actual_insured = player.insured
        
        self.assertEqual(expected_hand, actual_hand)
        self.assertEqual(expected_insured, actual_insured)        
    
    
    # Test Game.end().
    def test_end_player_wins(self):
        """If the player wins, the player gets double their initial 
        bet.
        """
        expected = 40
        
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Game(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    def test_end_player_loses(self):
        """If the player loses, the player loses their initial bet."""
        expected = 0
        
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(9, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Game(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.game.BaseUI.update')
    def test_end_tie(self, mock_update):
        """If the player ties, the player gets back their initial 
        bet.
        """
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        expected = 20
        expected_call = ['tie', player, [20, 20]]
        
        dhand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Game(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
        mock_update.assert_called_with(*expected_call)
    
    def test_end_player_blackjack(self):
        """If the player wins with a blackjack, they get two and a 
        half times their initial bet back.
        """
        expected = 50
        
        phand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(12, 1),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(13, 0),
            cards.Card(12, 3),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Game(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    def test_end_player_split_not_blackjack(self):
        """If the hand was split from aces it cannot be counted as 
        a blackjack.
        """
        expected = 40
        
        hand1 = cards.Hand([
            cards.Card(1, 1),
            cards.Card(10, 0),
        ])
        hand2 = cards.Hand([
            cards.Card(1, 2),
            cards.Card(2, 0),
            cards.Card(9, 1),
        ])
        player = players.Player([hand1, hand2], 'Michael', 0)
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Game(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    def test_end_with_ui(self):
        """Once the payout is determined, end() should send the event 
        to the UI.
        """
        cardlist = [
            cards.Card(7, 0, cards.UP),
            cards.Card(6, 0, cards.UP),
            cards.Card(5, 0, cards.UP),
        ]
        phand = cards.Hand(cardlist)
        player = players.AutoPlayer((phand,), 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.update('payout', player, [40, 220])]
        
        dhand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Game(None, dealer, (player,), ui, 20)
        g.end()
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)
    
    def test_end_with_ui(self):
        """Once the loss is determined, end() should send the event 
        to the UI.
        """
        cardlist = [
            cards.Card(7, 0, cards.UP),
            cards.Card(6, 0, cards.UP),
            cards.Card(10, 0, cards.UP),
        ]
        phand = cards.Hand(cardlist)
        player = players.AutoPlayer((phand,), 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.update('lost', player, [0, 180])]
        
        dhand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Game(None, dealer, (player,), ui, 20)
        g.end()
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)
    
    def test_end_split_with_ui(self):
        """Once the payout is determined, end() should send the event 
        to the UI. If the hand is split, that event should be 
        'splitpayout' if the hand wins.
        """
        hand2 = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        hand1 = cards.Hand([
            cards.Card(1, 2),
            cards.Card(2, 0),
            cards.Card(9, 1),
        ])
        player = players.Player([hand1, hand2], 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.update('splitpayout', player, [40, 220]),]
        
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Game(None, dealer, (player,), ui, 20)
        g.end()
        actual = [ui.mock_calls[-1],]
        
        self.assertEqual(expected, actual)
    
    def test_end_split_with_loss_ui(self):
        """Once the payout is determined, end() should send the event 
        to the UI. If the hand is split, that event should be 
        'splitlost' if the hand loses.
        """
        hand2 = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        hand1 = cards.Hand([
            cards.Card(1, 2),
            cards.Card(2, 0),
            cards.Card(9, 1),
        ])
        player = players.Player([hand2, hand1], 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.update('splitlost', player, [0, 220]),]
        
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Game(None, dealer, (player,), ui, 20)
        g.end()
        actual = [ui.mock_calls[-1],]
        
        self.assertEqual(expected, actual)
    
    def test_end_split_with_tie_ui(self):
        """Once the payout is determined, end() should send the event 
        to the UI. If the hand is split, that event should be 
        'splitlost' if the hand loses.
        """
        hand2 = cards.Hand([
            cards.Card(7, 1),
            cards.Card(10, 0),
        ])
        hand1 = cards.Hand([
            cards.Card(1, 2),
            cards.Card(2, 0),
            cards.Card(9, 1),
        ])
        player = players.Player([hand1, hand2], 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.update('splittie', player, [20, 200]),]
        
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Game(None, dealer, (player,), ui, 20)
        g.end()
        actual = [ui.mock_calls[-1],]
        
        self.assertEqual(expected, actual)
    
    def test_end_split_blackjack_with_ui(self):
        """Once the payout is determined, end() should send the event 
        to the UI. If the hand is split and it's a blackjack, the 
        event should be 'splitpayout'.
        """
        hand2 = cards.Hand([
            cards.Card(1, 1),
            cards.Card(10, 0),
        ])
        hand1 = cards.Hand([
            cards.Card(1, 2),
            cards.Card(2, 0),
            cards.Card(9, 1),
        ])
        player = players.Player([hand1, hand2], 'Michael', 180)
        
        # This looks a little weird. Shouldn't the hand be different 
        # between the first two call.updates() since the cards in the 
        # hand will be different at those points?
        # 
        # No. game.play() is sending the dealer's hand object to 
        # ui.update(), and we are testing to make sure the same 
        # hand is sent. Since objects are mutable, the hand has three 
        # cards in it when assertEqual() runs, so the expected hand 
        # needs to have all three cards, too.
        expected = [call.update('splitpayout', player, [40, 220])]
        
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Game(None, dealer, (player,), ui, 20)
        g.end()
        actual = [ui.mock_calls[-1],]
        
        self.assertEqual(expected, actual)
    
    def test_end_with_double_down(self):
        """If the hand was doubled down, the pay out should quadruple 
        the initial bet.
        """
        expected = 80
        
        phand = cards.Hand([
            cards.Card(4, 1),
            cards.Card(6, 2),
            cards.Card(10, 0),
        ])
        phand.doubled_down = True
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Game(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    def test_end_with_insured(self):
        """If the player was insured and the dealer had a blackjack, 
        the insurance pay out should double the insurance amount.
        """
        phand = cards.Hand([
            cards.Card(4, 1),
            cards.Card(6, 2),
            cards.Card(10, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        expected = [call.update('insurepay', player, [20, 20])]
        
        player.insured = 10
        dhand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        ui = Mock()
        g = game.Game(None, dealer, (player,), ui, 20)
        g.end()
        actual = [ui.mock_calls[-2],]
        
        self.assertEqual(expected, actual)
    
    def test_end_dealer_blackjack_player_21(self):
        """Given a dealer hand that is a blackjack, all players who 
        don't have blackjack lose.
        """
        expected = 0
        
        phand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(10, 0),
            cards.Card(9, 1),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Game(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        
        self.assertEqual(expected, actual)
    
    
    # Game._split() tests.
    def test__split_cannot_split(self):
        """Given a hand and a player, if the hand cannot be split, 
        _split() should not split it and return false.
        """
        expected_h1 = [cards.Hand([
            cards.Card(11, 3),
            cards.Card(2, 1),
        ]),]
        expected_return = False
        
        p1 = players.AutoPlayer(copy(expected_h1), name='John')
        playerlist = [p1,]
        g = game.Game(None, None, playerlist)
        actual_return = g._split(expected_h1[0], p1)
        actual_h1 = p1.hands
        
        self.assertEqual(expected_h1, actual_h1)
        self.assertEqual(expected_return, actual_return)
    
    def test__split_does_split(self):
        """Given a hand and a player, if the hand can be split and the 
        player says to split, the hand should be split, and the method 
        should return True.
        """
        expected_hands = (
            cards.Hand([cards.Card(11, 3),]),
            cards.Hand([cards.Card(11, 1),]),
        )
        expected_return = True
        exp_chips = 0
        
        h1 = [cards.Hand([
            cards.Card(11, 3),
            cards.Card(11, 1),
        ]),]
        p1 = players.AutoPlayer(copy(h1), 'John', 20)
        playerlist = [p1,]
        g = game.Game(None, None, playerlist, None, 20)
        actual_return = g._split(h1[0], p1)
        actual_hands = p1.hands
        act_chips = p1.chips
        
        self.assertEqual(expected_hands, actual_hands)
        self.assertEqual(expected_return, actual_return)
        self.assertEqual(exp_chips, act_chips)
    
    def test__split_with_ui(self):
        """If _split() splits the hand, it should send the event, 
        the player, and the new hand to the UI.
        """
        hands = (
            cards.Hand([cards.Card(11, 3),]),
            cards.Hand([cards.Card(11, 1),]),
        )
        h1 = [cards.Hand([
            cards.Card(11, 3),
            cards.Card(11, 1),
        ]),]
        p1 = players.AutoPlayer(copy(h1), 'John', 200)
        expected = ('split', p1, [20, 180])
        
        playerlist = [p1,]
        g = game.Game(None, None, playerlist, Mock(), 20)
        _ = g._split(h1[0], p1)

        g.ui.update.assert_called_with(*expected)
    
    
    # Test Game._ace_split_hit()
    def test__ace_split_hit(self):
        """Given a hand with an ace that had been split, 
        _ace_split_hit() should give hand one hit and then 
        stand.
        """
        expected = cards.Hand([
            cards.Card(1, 3),
            cards.Card(11, 0, cards.DOWN),
        ])
        
        deck = cards.Deck([
            expected[1],
        ])
        hand = cards.Hand([
            expected[0],
        ])
        player = players.AutoPlayer((hand,), name='Eric')
        g = game.Game(deck, None, (player,))
        g._ace_split_hit(player, hand)
        actual = player.hands[0]
        
        self.assertEqual(expected, actual)
    
    def test__ace_split_hit_ui(self):
        """Given a hand with an ace that had been split, 
        _ace_split_hit() should send an event to the UI 
        for the single hit and the stand.
        """
        hand = cards.Hand([
            cards.Card(1, 3),
        ])
        player = players.AutoPlayer([hand,], name='John')
        expected = [
            call.update('hit', player, hand),
            call.update('stand', player, hand),
        ]
        
        deck = cards.Deck([
            cards.Card(11, 0, cards.DOWN),
        ])
        ui = Mock()
        g = game.Game(deck, None, (player,), ui)
        g._ace_split_hit(player, hand)
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)
    
    
    # Test Game.start().
    def test_start_take_payment(self):
        """In a Game with players who will buy-in and a buy-in, 
        buyin() should take the buy-in from the player's chips 
        totals.
        """
        expected = 180.00
        
        p1 = players.AutoPlayer([], 'John', 200)
        p2 = players.AutoPlayer([], 'Michael', 200)
        playerlist = [p1, p2]
        g = game.Game(None, None, playerlist, None, 20.00)
        g.start()
        actual_p1 = p1.chips
        actual_p2 = p2.chips
        
        self.assertEqual(expected, actual_p1)
        self.assertEqual(expected, actual_p2)
    
    def test_start_too_few_chips(self):
        """If a player tries to buy into a game but does not have 
        enough chips, start() should remove them from the game and 
        add a new player.
        """
        expected = players.Player
        
        p1 = players.Player(name='John', chips = 1)
        g = game.Game(None, None, [p1,], None, 20)
        g.start()
        actual = g.playerlist[0]
        
        self.assertTrue(isinstance(actual, expected))
        self.assertNotEqual(expected, actual)
    
    def test_start_buyin_ui(self):
        """When a player buys into the round, start() should send that 
        event to the UI.
        """
        buyin = 20.00
        chips = 200
        p1 = players.AutoPlayer([], 'John', chips)
        p2 = players.AutoPlayer([], 'Michael', chips)
        expected = [
            call.update('buyin', p1, [buyin, chips - buyin]),
            call.update('buyin', p2, [buyin, chips - buyin]),
        ]
        
        playerlist = [p1, p2]
        ui = Mock()
        g = game.Game(None, None, playerlist, ui, buyin)
        g.start()
        actual = ui.mock_calls
        
        self.assertEqual(expected, actual)        
    
    @patch('blackjack.game.make_player')
    def test_start_remove_ui(self, mock_make_player):
        """When a player is removed, start() should send that event to 
        the UI and then send an event for the addition of the new 
        player.
        """
        unexp_player = players.AutoPlayer([], 'Eric', 1)
        exp_player = players.AutoPlayer([], 'Spam', 1)
        exp_calls = [
            call.update('remove', unexp_player, ''),
            call.update('join', exp_player, '')
        ]
        
        ui = Mock()
        mock_make_player.return_value = exp_player
        g = game.Game(playerlist=(unexp_player,), ui=ui, buyin=20)
        g.start()
        act_player = g.playerlist[0]
        act_calls = ui.mock_calls
        
        self.assertEqual(exp_player, act_player)
        self.assertEqual(exp_calls, act_calls)
    
    
    # Test Game._remove_player().
    def test__remove_player(self):
        """Given player, _remove_player() should remove that player 
        from the playlist attribute.
        """
        expected = [None,]
        
        p1 = players.Player(name='John', chips = 1)
        g = game.Game(None, None, [p1,], None, 20)
        g._remove_player(p1)
        actual = g.playerlist
        
        self.assertEqual(expected, actual)
    
    
    # Test Game._compare_score().
    def test__compare_score_player_win(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return True if the player's score is higher.
        """
        expected = True
        
        p_hand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(11, 3),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(7, 2),
        ])
        g = game.Game()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
    
    def test__compare_score_player_lose(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return False if the player's score is lower.
        """
        expected = False
        
        p_hand = cards.Hand([
            cards.Card(3, 1),
            cards.Card(11, 3),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(7, 2),
        ])
        g = game.Game()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
        
    def test__compare_score_player_bust(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return False if the player busts.
        """
        expected = False
        
        p_hand = cards.Hand([
            cards.Card(3, 1),
            cards.Card(11, 3),
            cards.Card(12, 2),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(7, 2),
        ])
        g = game.Game()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
        
    def test__compare_score_dealer_bust(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return True if the dealer busts.
        """
        expected = True
        
        p_hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(12, 2),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(6, 1),
            cards.Card(7, 2),
        ])
        g = game.Game()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
        
    def test__compare_score_tie(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return None if it is a tie.
        """
        expected = None
        
        p_hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(12, 2),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(5, 1),
            cards.Card(5, 2),
        ])
        g = game.Game()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
        
    def test__compare_score_dealer_wins_busts(self):
        """Given a player hand and a dealer hand, _compare_score() 
        should return True if the dealer busts.
        """
        expected = False
        
        p_hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(12, 2),
            cards.Card(13, 0),
        ])
        d_hand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(6, 1),
            cards.Card(7, 2),
        ])
        g = game.Game()
        actual = g._compare_score(d_hand, p_hand)
        
        self.assertEqual(expected, actual)
    
    
    # Test Game._double_down().
    def test__double_down(self):
        """Given a hand and a player who will double down and can 
        double down, _double_down() should set the doubled_down 
        attribute on the hand and take the player's additional bet.
        """
        expected_dd = True
        expected_chips = 0
        
        hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        g = game.Game(None, None, (player,), None, 20)
        g._double_down(player, hand)
        actual_dd = hand.doubled_down
        actual_chips = player.chips
        
        self.assertEqual(expected_dd, actual_dd)
        self.assertEqual(expected_chips, actual_chips)
    
    def test__double_down_ui(self):
        """If the player doubles down, _double_down() should send that 
        event to the UI.
        """
        hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        expected = ['doubled', player, [20, 0]]

        ui = Mock()
        g = game.Game(None, None, (player,), ui, 20)
        g._double_down(player, hand)
        
        ui.update.assert_called_with(*expected)
    
    def test__double_down_not_on_blackjack(self):
        """If player has a blackjack, _double_down() should not allow 
        the hand to be doubled down.
        """
        expected_dd = False
        expected_chips = 20
        
        hand = cards.Hand([
            cards.Card(1, 2),
            cards.Card(13, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        g = game.Game(None, None, (player,), None, 20)
        g._double_down(player, hand)
        actual_dd = hand.doubled_down
        actual_chips = player.chips
        
        self.assertEqual(expected_dd, actual_dd)
        self.assertEqual(expected_chips, actual_chips)
    
    
    # Test Game._insure()
    def test__insure(self):
        """Given a dealer hand a player can ensure and a player who 
        will insure, _insure() should set the insured attribute on 
        the player and take the player's additional bet.
        """
        expected_insured = 10
        expected_chips = 0
        
        dhand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        player = players.AutoPlayer(cards.Hand(), 'Eric', 10)
        g = game.Game(None, dealer, (player,), None, 20)
        g._insure(player)
        actual_insured = player.insured
        actual_chips = player.chips
        
        self.assertEqual(expected_insured, actual_insured)
        self.assertEqual(expected_chips, actual_chips)
    
    def test__insure_zero(self):
        """Given a dealer hand a player can ensure and a player who 
        will insure, _insure() should set the insured attribute on 
        the player and take the player's additional bet.
        """
        expected_insured = 0
        expected_chips = 10
        
        dhand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        player = players.BetterPlayer(cards.Hand(), 'Eric', 10)
        g = game.Game(None, dealer, (player,), None, 20)
        g._insure(player)
        actual_insured = player.insured
        actual_chips = player.chips
        
        self.assertEqual(expected_insured, actual_insured)
        self.assertEqual(expected_chips, actual_chips)
    
    def test__insure_ui(self):
        """If the player insures, _insure() should send that 
        event to the UI.
        """
        dhand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        player = players.AutoPlayer(None, 'Eric', 20)
        expected = ['insure', player, [10, 10]]

        ui = Mock()
        g = game.Game(None, dealer, (player,), ui, 20)
        g._insure(player)
        
        ui.update.assert_called_with(*expected)
    
    
    # Test Game._draw().
    def test__draw_deck_with_cards(self):
        """Draw a the top card from the game deck."""
        deck = cards.Deck.build(6)
        expected = deck[-1]
        
        g = game.Game(deck)
        actual = g._draw()
        
        self.assertEqual(expected, actual)
    
    def test__draw_deck_with_no_cards(self):
        """If the game deck has no card, create, shuffle, and cut a 
        new deck, then draw.
        """
        expected = cards.Card
        
        g = game.Game()
        g.deck = cards.Deck([])
        g.deck.size = 6
        actual = g._draw()
        
        self.assertTrue(isinstance(actual, expected))
    
    def test__draw_ui(self):
        """If the player insures, _insure() should send that 
        event to the UI.
        """
        dhand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        expected = ['shuffled', dealer, '']

        ui = Mock()
        g = game.Game(None, dealer, None, ui, 20)
        g.deck = cards.Deck([])
        g.deck.size = 6
        _ = g._draw()
        
        ui.update.assert_called_with(*expected)
    
    
    # Test Game._add_player().
    def test__add_player(self):
        """Given a player, _add_player() adds that player in the first 
        empty slot in the playerlist.
        """
        player = players.Player(name='Spam')
        expected = [player,]
        
        playerlist = [None,]
        g = game.Game(None, None, playerlist, None, None)
        g._add_player(player)
        actual = g.playerlist
        
        self.assertEqual(expected, actual)