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
import json
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
        """If no deck or deck size is given, a casino deck should be
        created and stored in the deck attribute.
        """
        expected_cls = cards.Deck
        expected_len = 52 * 6

        g = game.Engine()
        actual_cls = g.deck
        actual_len = len(g.deck)

        self.assertTrue(isinstance(actual_cls, expected_cls))
        self.assertEqual(expected_len, actual_len)

    def test_deck_size_given(self):
        """Given a deck size and no deck and no random cut, game.Engine
        should construct a deck of the given size.
        """
        # Expected values.
        expected_cls = cards.Deck
        expected_len = 52 * 3

        # Test data and state.
        deck_size = 3

        # Run test.
        g = game.Engine(deck_size=deck_size)

        # Gather actual data.
        actual_cls = g.deck
        actual_len = len(g.deck)

        # Determine test results
        self.assertTrue(isinstance(actual_cls, expected_cls))
        self.assertEqual(expected_len, actual_len)

    @patch('blackjack.cards.randrange', return_value=65)
    def test_deck_cut_given(self, _):
        """If the deck_cut parameter is true, the deck should
        be cut.
        """
        # Expected values.
        expected_cls = cards.Deck
        expected_len = 52 * 6 - 65

        # Test data and state.
        deck_cut = True

        # Run test.
        g = game.Engine(deck_cut=deck_cut)

        # Get actuals.
        actual_cls = g.deck
        actual_len = len(g.deck)

        # Determine test results.
        self.assertIsInstance(actual_cls, expected_cls)
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
        expected = game.BaseUI

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

    @patch('blackjack.game.ValidUI.validate', return_value=Mock())
    def test__ace_split_hit_ui(self, _):
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
        g = game.Engine(deck, None, (player,))
        g._ace_split_hit(player, hand)
        actual = g.ui.mock_calls

        self.assertEqual(expected, actual)

    # Test Engine._add_player().
    def test__add_player(self):
        """Given a player, _add_player() adds that player in the first
        empty slot in the playerlist.
        """
        player = players.Player(name='Spam')
        expected = (player,)

        playerlist = [None,]
        g = game.Engine(None, None, playerlist, None, None)
        g._add_player(player)
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

    # Test Engine._deserialize().
    def test__deserialize(self):
        """When given a serialized Engine object, _deserialize()
        should change the attributes of the current Engine object
        to match the serialized object's attributes.
        """
        deck2 = cards.Deck([
            cards.Card(11, 3, True),
        ])
        dealer2 = players.Dealer(name='ham')
        exp_before = {
            'class': 'Engine',
            'buyin': 0,
            'card_count': 0,
            'deck': deck2.serialize(),
            'deck_size': deck2.size,
            'dealer': dealer2.serialize(),
            'playerlist': [],
            'save_file': 'baked.beans',
        }

        deck = cards.Deck([
            cards.Card(11, 0, True),
            cards.Card(11, 1, True),
            cards.Card(11, 2, True),
        ])
        dealer = players.Dealer(name='spam')
        player1 = players.AutoPlayer(name='eggs')
        player2 = players.AutoPlayer(name='bacon')
        exp_after = {
            'class': 'Engine',
            'buyin': 200,
            'card_count': 7,
            'deck': deck.serialize(),
            'deck_size': deck.size,
            'dealer': dealer.serialize(),
            'playerlist': [
                player1.serialize(),
                player2.serialize(),
            ],
            'save_file': 'tomato',
        }

        g = game.Engine(deck2, dealer2, (), None, 0, 'baked.beans')
        text_before = g.serialize()
        act_before = json.loads(text_before)
        g._deserialize(json.dumps(exp_after))
        text_after = g.serialize()
        act_after = json.loads(text_after)

        self.assertDictEqual(exp_before, act_before)
        self.assertDictEqual(exp_after, act_after)

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

    @patch('blackjack.game.BaseUI.doubledown')
    def test__double_down_ui(self, mock_dd):
        """If the player doubles down, _double_down() should send that
        event to the UI.
        """
        hand = cards.Hand([
            cards.Card(4, 2),
            cards.Card(6, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        expected = (player, 20)

        g = game.Engine(None, None, (player,), None, 20)
        g._double_down(player, hand)

        mock_dd.assert_called_with(*expected)

    @patch('blackjack.players.AutoPlayer.will_double_down', return_value=True)
    def test__double_down_not_on_blackjack(self, mock_willdd):
        """If player has a blackjack, _double_down() should not allow
        the hand to be doubled down.
        """
        expected_dd = False
        expected_chips = 20
        exp_calls = []

        hand = cards.Hand([
            cards.Card(1, 2),
            cards.Card(13, 3),
        ])
        player = players.AutoPlayer([hand,], 'Eric', 20)
        g = game.Engine(None, None, (player,), None, 20)
        g._double_down(player, hand)
        actual_dd = hand.doubled_down
        actual_chips = player.chips
        act_calls = mock_willdd.mock_calls

        self.assertEqual(expected_dd, actual_dd)
        self.assertEqual(expected_chips, actual_chips)
        self.assertListEqual(exp_calls, act_calls)

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
        # Expected values.
        cards_per_deck = 52
        num_decks = 6
        num_drawn = 1
        expected = cards.Card
        exp_num_cards = cards_per_deck * num_decks - num_drawn

        # Test data and state.
        card_count = 20
        g = game.Engine(card_count=card_count)
        g.deck = cards.Deck([])
        g.deck.size = num_decks

        # Run test.
        actual = g._draw()
        act_num_cards = len(g.deck)
        act_count = g.card_count

        # Determine test result.
        self.assertIsInstance(actual, expected)
        self.assertEqual(exp_num_cards, act_num_cards)
        if actual.rank == 1 or actual.rank >= 10:
            self.assertEqual(act_count, 1)
        elif actual.rank <= 6:
            self.assertEqual(act_count, -1)
        else:
            self.assertEqual(act_count, 0)

    @patch('blackjack.cards.randrange', return_value=65)
    def test__draw_deck_with_no_cards_with_deck_cut(self, mock_randrange):
        """If the game deck has no card, create, shuffle, and cut a
        new deck, then draw.
        """
        # Expected values.
        cards_per_deck = 52
        num_decks = 6
        num_cut = mock_randrange()
        num_drawn = 1
        expected = cards.Card
        exp_num_cards = cards_per_deck * num_decks - num_cut - num_drawn

        # Test data and state.
        g = game.Engine(deck_cut=True)
        g.deck = cards.Deck([])
        g.deck.size = num_decks

        # Run test.
        actual = g._draw()
        act_num_cards = len(g.deck)

        # Determine test result.
        self.assertIsInstance(actual, expected)
        self.assertEqual(exp_num_cards, act_num_cards)

    @patch('blackjack.game.BaseUI.shuffles')
    def test__draw_shuffled_ui(self, mock_shuffles):
        """If the deck is shuffled, _draw() should send that
        event to the UI.
        """
        dhand = cards.Hand([
            cards.Card(1, 1),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer')
        ui = Mock()
        g = game.Engine(None, dealer, None, None, 20)
        g.deck = cards.Deck([])
        g.deck.size = 6
        _ = g._draw()

        mock_shuffles.assert_called()

    def test__draw_updates_count(self):
        """Drawing a card from the deck should update the count."""
        # Expected value.
        exp = 2

        # Test data and state.
        deck = cards.Deck([
            cards.Card(11, 0),
            cards.Card(8, 1),
            cards.Card(12, 3),
            cards.Card(2, 0),
            cards.Card(1, 2),
        ])
        g = game.Engine(deck)

        # Run test.
        while g.deck:
            _ = g._draw()

        # Gather actual data.
        act = g.card_count

        # Determine test result.
        self.assertEqual(exp, act)

    # Test Engine._hit().
    @patch('blackjack.players.AutoPlayer.will_hit', return_value=True)
    @patch('blackjack.game.BaseUI.hit')
    def test__hit_no_hit_on_blackjack(self, mock_hit, _):
        """Given a natural blackjack hand, hit should stand."""
        exp = []

        hand = cards.Hand((
            cards.Card(11, 3),
            cards.Card(1, 3),
        ))
        player = players.AutoPlayer((hand,), name='spam')
        g = game.Engine()
        g._hit(player, hand)
        act = mock_hit.mock_calls

        self.assertListEqual(exp, act)

    @patch('blackjack.players.AutoPlayer.will_hit', return_value=True)
    @patch('blackjack.game.BaseUI.hit')
    def test__hit_no_hit_on_bust(self, mock_hit, _):
        """Given a busted hand, hit should stand."""
        exp = []

        hand = cards.Hand((
            cards.Card(11, 3),
            cards.Card(11, 3),
            cards.Card(11, 3),
        ))
        player = players.AutoPlayer((hand,), name='spam')
        g = game.Engine()
        g._hit(player, hand)
        act = mock_hit.mock_calls

        self.assertListEqual(exp, act)

    # Test Engine._insure().
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

    @patch('blackjack.game.BaseUI.insures')
    def test__insure_ui(self, mock_insures):
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
        g = game.Engine(None, dealer, (player,), None, 20)
        g._insure(player)

        mock_insures.assert_called_with(*expected)

    # Test Engine._remove_player().
    def test__remove_player(self):
        """Given player, _remove_player() should remove that player
        from the playlist attribute.
        """
        expected = (None,)

        p1 = players.Player(name='John', chips=1)
        g = game.Engine(None, None, [p1,], None, 20)
        g._remove_player(p1)
        actual = g.playerlist

        self.assertEqual(expected, actual)

    # Engine._split() tests.
    def test__split_cannot_split(self):
        """Given a hand and a player, if the hand cannot be split,
        _split() should not split it and return false.
        """
        expected_h1 = (cards.Hand([
            cards.Card(11, 3),
            cards.Card(2, 1),
        ]),)
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

    @patch('blackjack.game.BaseUI.splits')
    def test__split_with_ui(self, mock_splits):
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
        g = game.Engine(None, None, playerlist, None, 20)
        _ = g._split(h1[0], p1)

        mock_splits.assert_called_with(*expected)

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

    @patch('blackjack.game.BaseUI.deal')
    def test_deal_with_ui(self, mock_deal):
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

        deck = cards.Deck(cardlist)
        g = game.Engine(dealer=dealer)
        g.deck = deck
        g.deal()

        mock_deal.assert_called_with(*expected)

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

    # Test Engine.new_game().
    @patch('blackjack.game.BaseUI.joins')
    def test_new_game_players_join(self, mock_joins):
        """When players join a game, it should send a join
        event to the UI for each player in the game.
        """
        playerlist = [
            players.Player(),
            players.Player(),
            players.Player(),
        ]
        e = game.Engine(playerlist=playerlist)
        expected = [
            call(e.dealer),
            call(playerlist[0]),
            call(playerlist[1]),
            call(playerlist[2]),
        ]

        e.new_game()
        actual = mock_joins.mock_calls

        self.assertListEqual(expected, actual)

    # Test Engine.end().
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

    def test_end_dealer_blackjack_player_split_21(self):
        """Given a dealer hand that is a blackjack, all players who
        don't have blackjack lose, including those with split hands.
        """
        expected = 0

        phand = cards.Hand([
            cards.Card(5, 0),
            cards.Card(5, 0),
            cards.Card(1, 1),
        ])
        ohand = cards.Hand([
            cards.Card(2, 1),
            cards.Card(10, 0),
            cards.Card(9, 1),
        ])
        player = players.AutoPlayer((ohand, phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips

        self.assertEqual(expected, actual)

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

    def test_end_player_blackjack_dealer_21(self):
        """If the player wins with a blackjack, they get two and a
        half times their initial bet back, even if the dealer has 21
        on more than 2 cards.
        """
        expected = 50

        phand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(12, 1),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        dhand = cards.Hand([
            cards.Card(1, 0),
            cards.Card(6, 3),
            cards.Card(4, 3),
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

    @patch('blackjack.game.BaseUI.wins_split')
    def test_end_split_blackjack_with_ui(self, mock_wins):
        """Once the payout is determined, end() should send the event
        to the UI. If the hand is split and it's a blackjack, the
        event should be wins_split().
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
        expected = call(player, 40)

        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = mock_wins.mock_calls[-1]

        self.assertEqual(expected, actual)

    @patch('blackjack.game.BaseUI.loses_split')
    def test_end_split_with_loss_ui(self, mock_loses):
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
        expected = call(player)

        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = mock_loses.mock_calls[-1]

        self.assertEqual(expected, actual)

    @patch('blackjack.game.BaseUI.ties_split')
    def test_end_split_with_tie_ui(self, mock_ties_split):
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
        expected = call(player, 20)

        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = mock_ties_split.mock_calls[-1]

        self.assertEqual(expected, actual)

    @patch('blackjack.game.BaseUI.wins_split')
    def test_end_split_with_ui(self, mock_split):
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
        expected = call(player, 40)

        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = mock_split.mock_calls[-1]

        self.assertEqual(expected, actual)

    @patch('blackjack.game.BaseUI.tie')
    def test_end_tie_with_ui(self, mock_tie):
        """If the player ties, the player gets back their initial
        bet.
        """
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        expected = 20
        expected_call = call(player, 20)

        dhand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = player.chips
        actual_call = mock_tie.mock_calls[-1]

        self.assertEqual(expected, actual)
        self.assertEqual(expected_call, actual_call)

    @patch('blackjack.game.BaseUI.insurepay')
    def test_end_with_insured(self, mock_insurepay):
        """If the player was insured and the dealer had a blackjack,
        the insurance pay out should double the insurance amount.
        """
        phand = cards.Hand([
            cards.Card(4, 1),
            cards.Card(6, 2),
            cards.Card(10, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        expected = call(player, 20)

        player.insured = 10
        dhand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = mock_insurepay.mock_calls[-1]

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

    @patch('blackjack.game.BaseUI.loses')
    def test_end_with_ui_loses(self, mock_loses):
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
        expected = call(player)

        dhand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = mock_loses.mock_calls[-1]

        self.assertEqual(expected, actual)

    @patch('blackjack.game.BaseUI.wins')
    def test_end_with_ui_won(self, mock_wins):
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
        expected = call(player, 40)

        dhand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 20)
        g.end()
        actual = mock_wins.mock_calls[-1]

        self.assertEqual(expected, actual)

    # Engine.play() tests.
    def test_play_bust(self):
        """In a Engine object with a deck and a dealer with a dealt
        hand, play() should deal cards to the dealer until the dealer
        stands on a bust.
        """
        expected = (
            cards.Card(2, 1),
            cards.Card(3, 2),
            cards.Card(6, 0),
            cards.Card(5, 1),
            cards.Card(11, 3),
        )

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
        expected = (
            cards.Card(10, 1),
            cards.Card(3, 2),
            cards.Card(7, 0),
        )

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
        dealer = players.Dealer(name='Dealer')
        dealer.hands = [cards.Hand([
            cards.Card(5, 0),
            cards.Card(5, 1),
        ]),]
        player = players.AutoPlayer(name='Player')
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

    @patch('blackjack.game.ValidUI.validate', return_value=Mock())
    def test_play_with_ui(self, mock_valid):
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
        g = game.Engine(dealer=dealer)
        g.deck = deck
        g.play()
        actual = g.ui.mock_calls

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

    # Test Engine,restore().
    @patch('blackjack.game.ValidUI.validate')
    @patch('blackjack.game.BaseUI')
    @patch('blackjack.game.open')
    def test_restore(self, mock_open, mock_ui, mock_valid):
        """When called, restore() should load the serialized instance
        of Engine from file, set the current object's attributes to
        those of the serialized object, and reset the UI.
        """
        deck = cards.Deck([
            cards.Card(11, 0, True),
            cards.Card(11, 1, True),
            cards.Card(11, 2, True),
        ])
        dealer = players.Dealer(name='spam')
        player1 = players.AutoPlayer(name='eggs')
        player2 = players.AutoPlayer(name='bacon')
        exp_attrs = json.dumps({
            'class': 'Engine',
            'buyin': 200,
            'card_count': 0,
            'deck': deck.serialize(),
            'deck_size': 6,
            'dealer': dealer.serialize(),
            'playerlist': [
                player1.serialize(),
                player2.serialize(),
            ],
            'save_file': 'save.json',
        })
        mock_open().__enter__().read.return_value = exp_attrs

        exp_open = [
            call(),
            call().__enter__(),
            call('save.json', 'r'),
            call().__enter__(),
            call().__enter__().read(),
            call().__exit__(None, None, None),
        ]
        exp_ui = [
            call(),
            call(),
            call().reset(),
            call().joins(players.Dealer(name='spam')),
            call().joins(players.AutoPlayer(name='eggs')),
            call().joins(players.AutoPlayer(name='bacon')),
        ]

        mock_valid.return_value = game.BaseUI()
        g = game.Engine()
        g.restore()
        act_open = mock_open.mock_calls
        act_ui = mock_ui.mock_calls
        act_attrs = g.serialize()

        self.assertListEqual(exp_open, act_open)
        self.assertListEqual(exp_ui, act_ui)
        self.assertEqual(exp_attrs, act_attrs)

    # Test Engine.save().
    @patch('blackjack.game.open')
    def test_save(self, mock_open):
        """When called, save() should serialize the Engine object and
        write it to a file.
        """
        deck = cards.Deck([
            cards.Card(11, 0, True),
            cards.Card(11, 1, True),
            cards.Card(11, 2, True),
        ])
        dealer = players.Dealer(name='spam')
        player1 = players.AutoPlayer(name='eggs')
        player2 = players.AutoPlayer(name='bacon')
        g = game.Engine(deck, dealer, (player1, player2,), None, 200)
        serial = g.serialize()
        exp = [
            call('save.json', 'w'),
            call().__enter__(),
            call().__enter__().write(serial),
            call().__exit__(None, None, None),
        ]

        g.save()
        act = mock_open.mock_calls

        self.assertListEqual(exp, act)

    # Test Engine.serialize().
    def test_serialize(self):
        """When called, serialize should return the object
        serialized as a JSON string.
        """
        deck = cards.Deck([
            cards.Card(11, 0, True),
            cards.Card(11, 1, True),
            cards.Card(11, 2, True),
        ])
        dealer = players.Dealer(name='spam')
        player1 = players.AutoPlayer(name='eggs')
        player2 = players.AutoPlayer(name='bacon')
        exp = {
            'class': 'Engine',
            'buyin': 200,
            'card_count': 0,
            'deck': deck.serialize(),
            'deck_size': deck.size,
            'dealer': dealer.serialize(),
            'playerlist': [
                player1.serialize(),
                player2.serialize(),
            ],
            'save_file': 'ham',
        }

        g = game.Engine(deck, dealer, (player1, player2,), None, 200, 'ham')
        text = g.serialize()
        act = json.loads(text)

        self.assertDictEqual(exp, act)

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
        expected = players.AutoPlayer

        p1 = players.AutoPlayer(name='John', chips=1)
        g = game.Engine(None, None, [p1,], None, 20)
        g.start()
        actual = g.playerlist[0]

        self.assertFalse(isinstance(actual, expected))

    def test_start_buyin_false(self):
        """If a player chooses not to buyin, start() should remove
        them from the game and add a new player.
        """
        p1 = players.NeverPlayer(name='John', chips=40)
        exp = (p1,)

        g = game.Engine(None, None, exp, None, 20)
        g.start()
        act = g.playerlist

        self.assertNotEqual(exp, act)

    @patch('blackjack.game.BaseUI.bet')
    def test_start_buyin_ui(self, mock_bet):
        """When a player buys into the round, start() should send that
        event to the UI.
        """
        buyin = 20.00
        chips = 200
        p1 = players.AutoPlayer([], 'John', chips)
        p2 = players.AutoPlayer([], 'Michael', chips)
        expected = [
            call(p1, buyin),
            call(p2, buyin),
        ]

        playerlist = [p1, p2]
        g = game.Engine(None, None, playerlist, None, buyin)
        g.start()
        actual = g.ui.bet.mock_calls

        self.assertEqual(expected, actual)

    @patch('blackjack.game.BaseUI.joins')
    @patch('blackjack.game.BaseUI.leaves')
    @patch('blackjack.game.make_player')
    def test_start_remove_ui(self, mock_make_player, mock_leaves, mock_joins):
        """When a player is removed, start() should send that event to
        the UI and then send an event for the addition of the new
        player.
        """
        unexp_player = players.AutoPlayer([], 'Eric', 1)
        exp_player = players.AutoPlayer([], 'Spam', 1)
        exp_calls = [
            call(unexp_player),
            call(exp_player),
        ]

        ui = game.BaseUI()
        mock_make_player.return_value = exp_player
        g = game.Engine(playerlist=(unexp_player,), ui=ui, buyin=20)
        g.start()
        act_player = g.playerlist[0]
        act_calls = [
            ui.leaves.mock_calls[0],
            ui.joins.mock_calls[0],
        ]

        self.assertEqual(exp_player, act_player)
        self.assertEqual(exp_calls, act_calls)


class mainTestCase(ut.TestCase):
    def test_init_with_params(self):
        """main() should accept the following parameters: engine,
        is_interactive.
        """
        g = game.Engine()

        # This call will fail if the parameters are not accepted.
        game.main(g, is_interactive=False)

    @patch('blackjack.game.Engine')
    def test_call_game_phases(self, mock_engine):
        """main() should call each phase of a backjack game in the
        Engine object.
        """
        playerlist = [
            players.AutoPlayer(name='spam'),
            players.AutoPlayer(name='eggs'),
        ]
        exp = [
            call(playerlist=playerlist, buyin=2, save_file='bacon'),
            call().ui.start(is_interactive=True),
            call().new_game(),
            call().start(),
            call().deal(),
            call().play(),
            call().end(),
            call().save('bacon'),
            call().ui.nextgame_prompt(),
            call().ui.cleanup(),
            call().ui.nextgame_prompt().value.__bool__(),
            call().start(),
            call().deal(),
            call().play(),
            call().end(),
            call().save('bacon'),
            call().ui.nextgame_prompt(),
        ]

        g = game.Engine(playerlist=playerlist, buyin=2, save_file='bacon')
        g.save_file = 'bacon'
        loop = game.main(g)
        result = next(loop)
        result = loop.send(result)
        _ = loop.send(result)
        act = mock_engine.mock_calls

        self.assertListEqual(exp, act)


class validate_uiTestCase(ut.TestCase):
    def test_valid(self):
        """Given a valid value, validate_ui() should return it."""
        exp = game.BaseUI()
        act = game.validate_ui(None, exp)
        self.assertEqual(exp, act)

    def test_invalid(self):
        """Given an invalid value, validate_ui() should raise a
        ValueError exception.
        """
        exp = ValueError

        class Eggs:
            msg = '{}'
        test = 'spam'

        with self.assertRaises(exp):
            _ = game.validate_ui(Eggs(), test)
