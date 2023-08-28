"""
test_game.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.game module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import inspect
import json
import unittest as ut
from copy import copy, deepcopy
from functools import partial
from itertools import zip_longest
from random import seed
from unittest.mock import Mock, call, patch
from types import MethodType

import pytest

from blackjack import cli, cards, game, players


# Utility functions.
def loopback(value):
    """Return whatever is sent to it."""
    return value


# Test cases.
# Engine test cases.
# Fixtures for Engine.
@pytest.fixture
def deck(request):
    """Create a :class:`Deck` object for testing."""
    marker = request.node.get_closest_marker('deck')
    cardlist = [cards.Card(*args) for args in marker.args]
    yield cards.Deck(cardlist)


@pytest.fixture
def engine(mocker):
    """Create a :class:`Engine` object for testing."""
    mocker.patch(
        'blackjack.game.ValidUI.validate',
        return_value=mocker.Mock()
    )
    yield game.Engine(buyin=20)


@pytest.fixture
def hand(request):
    """Create a :class:`Hand` object for testing."""
    marker = request.node.get_closest_marker('hand')
    cardlist = [cards.Card(*args) for args in marker.args]
    yield cards.Hand(cardlist)


@pytest.fixture
def hands(request):
    """Create a :class:`Hand` object for testing."""
    marker = request.node.get_closest_marker('hands')
    hands = []
    for item in marker.args:
        cardlist = [cards.Card(*args) for args in item]
        hands.append(cards.Hand(cardlist))
    return hands


@pytest.fixture
def player():
    """Create a :class:`AutoPlayer` object for testing."""
    return players.AutoPlayer(name='Eric', chips=100)


# Tests for Engine class methods.
def test_Engine_deserialize():
    """Given a serialized :class:`Engine` object, deserialize and
    return the object.
    """
    dealer = players.Dealer(name='Spam')
    deck = cards.Deck.build(4)
    user = players.AutoPlayer(name='You')
    attrs = {
        'class': 'Engine',
        'bet_max': 50,
        'bet_min': 2,
        'buyin': 10,
        'card_count': 3,
        'deck': deck.serialize(),
        'deck_cut': True,
        'deck_size': 4,
        'dealer': dealer.serialize(),
        'playerlist': (
            user.serialize(),
        ),
        'running_count': True,
        'save_file': 'eggs.json',
    }
    s = json.dumps(attrs)
    attrs['dealer'] = dealer
    attrs['deck'] = deck
    attrs['playerlist'] = (user,)
    del attrs['class']
    engine = game.Engine.deserialize(s)
    for attr in attrs:
        assert getattr(engine, attr) == attrs[attr]


# Tests for Engine initialization.
def test_Engine_init_all_defaults():
    """Given no parameters, the attributes of the :class:`Engine`
    object should be set to default values.
    """
    # Creation of the deck involves random behavior, so seed the RNG,
    # create the expected deck, then seed the RNG with the same seed.
    seed('spam')
    deck = cards.Deck.build(6)
    deck.shuffle()
    seed('spam')

    optionals = {
        'bet_max': 500,
        'bet_min': 20,
        'buyin': 0,
        'card_count': 0,
        'deck': deck,
        'deck_cut': False,
        'deck_size': 6,
        'dealer': players.Dealer(name='Dealer'),
        'playerlist': (),
        'running_count': False,
        'save_file': 'save.json',
        'ui': game.BaseUI(),
    }
    engine = game.Engine()
    for attr in optionals:
        assert getattr(engine, attr) == optionals[attr]


def test_Engine_init_all_optionals():
    """Given parameters, the attributes of the :class:`Engine`
    object should be set to given values.
    """
    optionals = {
        'bet_max': 50,
        'bet_min': 2,
        'buyin': 10,
        'card_count': 3,
        'deck': cards.Deck.build(4),
        'deck_cut': True,
        'deck_size': 4,
        'dealer': players.Dealer(name='Spam'),
        'playerlist': (
            players.UserPlayer(name='You'),
        ),
        'running_count': True,
        'save_file': 'eggs.json',
        'ui': cli.LogUI(),
    }
    engine = game.Engine(**optionals)
    for attr in optionals:
        assert getattr(engine, attr) == optionals[attr]


def test_Engine_init_deck_size_without_deck():
    """Given a deck size and no deck and no random cut, :class:`Engine`
    should construct a deck of the given size.
    """
    seed('spam')
    deck = cards.Deck.build(3)
    deck.shuffle()
    seed('spam')

    engine = game.Engine(deck_size=3)
    assert engine.deck_size == 3
    assert engine.deck == deck


def test_Engine_init_deck_size_and_deck_cut_without_deck():
    """Given a deck sie and random cut, :class:`Engine` should
    construct a deck of the given size with a random cut.
    """
    seed('spam')
    deck = cards.Deck.build(5)
    deck.shuffle()
    deck.random_cut()
    seed('spam')

    engine = game.Engine(deck_size=5, deck_cut=True)
    assert engine.deck_size == 5
    assert engine.deck_cut
    assert engine.deck == deck


# Tests for Engine private methods.
@pytest.mark.deck([11, 0, False])
@pytest.mark.hands(
    [[1, 3],],
    [[1, 3], [11, 0, False]]
)
def test_Engine__ace_split_hit(mocker, deck, engine, hands, player):
    """Given a hand with an ace that had been split,
    :meth:`Engine._ace_split_hit` should give hand one
    hit and then stand.
    """
    hand, expected = hands
    player.hands = (hand,)
    engine.deck = deck
    engine._ace_split_hit(player, hand)
    assert player.hands[0] == expected
    assert engine.ui.mock_calls == [
        mocker.call.hit(player, hand),
        mocker.call.stand(player, hand),
    ]


def test_Engine__add_player(engine, player):
    """Given a player, :meth:`Engine._add_player` adds that player in
    the first empty slot in the playerlist.
    """
    engine.playerlist = [None,]
    engine._add_player(player)
    assert engine.playerlist == (player,)


@pytest.mark.hands(
    [[10, 3], [7, 2]],
    [[10, 1], [11, 3]]
)
def test_Engine__compare_score_player_wins(engine, hands):
    """Given a player hand and a dealer hand,
    :meth:`Engine._compare_score` should return
    `True` if the player's score is higher.
    """
    dhand, phand = hands
    assert engine._compare_score(dhand, phand)


@pytest.mark.hands(
    [[10, 1], [11, 3]],
    [[10, 3], [7, 2]]
)
def test_Engine__compare_score_player_loses(engine, hands):
    """Given a player hand and a dealer hand,
    :meth:`Engine._compare_score` should return
    `False` if the player's score is lower.
    """
    dhand, phand = hands
    assert engine._compare_score(dhand, phand) is False


@pytest.mark.hands(
    [[10, 1], [11, 3]],
    [[10, 3], [7, 2], [6, 2]]
)
def test_Engine__compare_score_player_busts(engine, hands):
    """Given a player hand and a dealer hand,
    :meth:`Engine._compare_score` should return
    `False` if the player busts.
    """
    dhand, phand = hands
    assert engine._compare_score(dhand, phand) is False


@pytest.mark.hands(
    [[10, 1], [11, 3], [10, 0]],
    [[10, 3], [7, 2]]
)
def test_Engine__compare_score_dealer_busts(engine, hands):
    """Given a player hand and a dealer hand,
    :meth:`Engine._compare_score` should return
    `True` if the dealer busts.
    """
    dhand, phand = hands
    assert engine._compare_score(dhand, phand)


@pytest.mark.hands(
    [[10, 1], [11, 3]],
    [[10, 3], [12, 2]]
)
def test_Engine__compare_score_tie(engine, hands):
    """Given a player hand and a dealer hand,
    :meth:`Engine._compare_score` should return
    `None` if it's a tie.
    """
    dhand, phand = hands
    assert engine._compare_score(dhand, phand) is None


@pytest.mark.hands(
    [[10, 1], [11, 3], [7, 3]],
    [[10, 3], [12, 2], [7, 0]]
)
def test_Engine__compare_both_bust(engine, hands):
    """Given a player hand and a dealer hand,
    :meth:`Engine._compare_score` should return
    `Fale` if both bust.
    """
    dhand, phand = hands
    assert engine._compare_score(dhand, phand) is False


@pytest.mark.hand([4, 2], [6, 3])
def test_Engine__double_down(mocker, engine, hand, player):
    """Given a hand and a player who will double down and can
    double down, :meth:`Engine._double_down` should set
    :attr:`Hand.doubled_down` on the hand and take the player's
    additional bet.
    """
    player.hands = [hand,]
    engine._double_down(player, hand)
    assert hand.doubled_down
    assert player.chips == 80
    assert engine.ui.mock_calls == [
        mocker.call.doubledown(player, 20)
    ]


@pytest.mark.hand([1, 2], [11, 3])
def test_Engine__double_down(mocker, engine, hand, player):
    """Given a hand with blackjack and a player who will double
    down, :meth:`Engine._double_down` should not allow the double
    down.
    """
    player.hands = [hand,]
    engine._double_down(player, hand)
    assert not hand.doubled_down
    assert player.chips == 100
    assert engine.ui.mock_calls == []


def test_Engine__draw(mocker, engine):
    """When called, :meth:`Engine._draw` should draw the top card
    of the deck.
    """
    seed('spam')
    engine.deck = cards.Deck([])
    assert engine._draw() == cards.Card(4, 0, False)
    assert len(engine.deck) == 52 * 6 - 1
    assert engine.ui.mock_calls == [
        mocker.call.shuffles(engine.dealer),
    ]


def test_Engine__draw_with_no_card(engine):
    """If the game deck has no card, :meth:`Engine._draw` should
    create, shuffle, and cut a new deck, then draw.
    """
    seed('spam')
    deck = cards.Deck.build(6)
    deck.shuffle()
    top_card = deck.draw()
    seed('spam')

    engine.deck = cards.Deck([])
    assert engine._draw() == top_card
    assert engine.deck == deck


def test_Engine__draw_with_no_card_and_random_cut(engine):
    """If the game deck has no card, :meth:`Engine._draw` should
    create, shuffle, and cut a new deck, then draw.
    """
    seed('spam')
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    top_card = deck.draw()
    seed('spam')

    engine.deck = cards.Deck([])
    engine.deck_cut = True
    assert engine._draw() == top_card
    assert engine.deck == deck


def test_Engine__draw_updates_count(mocker, engine):
    """When called, :meth:`Engine._draw` should draw the top card
    of the deck. If the engine is counting cards, drawing a card
    should update the count.
    """
    seed('spam')
    engine.deck = cards.Deck([])
    engine.running_count = True
    assert engine._draw() == cards.Card(4, 0, False)
    assert len(engine.deck) == 52 * 6 - 1
    assert engine.ui.mock_calls == [
        mocker.call.shuffles(engine.dealer),
        mocker.call.update_count(1),
    ]


@pytest.mark.hand([11, 3], [1, 3])
def test_Engine__hit_no_hit_on_blackjack(mocker, engine, hand, player):
    """Given a natural blackjack hand, hit should stand."""
    player.hands = (hand,)
    engine._hit(player, hand)
    assert engine.ui.mock_calls == [
        mocker.call.stand(player, hand),
    ]


@pytest.mark.hand([11, 3], [11, 3], [11, 3])
def test_Engine__hit_no_hit_on_blackjack(mocker, engine, hand, player):
    """Given a busted hand, hit should stand."""
    player.hands = (hand,)
    engine._hit(player, hand)
    assert engine.ui.mock_calls == [
        mocker.call.stand(player, hand),
    ]


@pytest.mark.hand([1, 1], [11, 0])
def test_Engine__insure(mocker, engine, hand, player):
    """Given a dealer hand a player can insure and a player who
    will insure, :meth:`Engine._insure` should set the insured
    attribute on the player and take the player's additional bet.
    """
    player.bet = 20
    player.hands = (cards.Hand(),)
    engine.dealer.hands = (hand,)
    engine._insure(player)
    assert player.insured == 10
    assert player.chips == 90
    assert engine.ui.mock_calls == [
        mocker.call.insures(player, 10),
    ]


@pytest.mark.hand([1, 1], [11, 0])
def test_Engine__insure_zero(engine, hand):
    """Given a dealer hand a player can insure and a player who
    will not insure, :meth:`Engine._insure` should set the insured
    attribute on the player and take the player's additional bet.
    """
    player = players.BetterPlayer(name='Eric', chips=100)
    player.bet = 20
    player.hands = (cards.Hand(),)
    engine.dealer.hands = (hand,)
    engine._insure(player)
    assert player.insured == 0
    assert player.chips == 100
    assert engine.ui.mock_calls == []


def test_Engine__remove_player(engine, player):
    """Given player, :meth:`Engine._remove_player` should remove that
    player from the playlist attribute.
    """
    engine.playerlist = (player,)
    engine._remove_player(player)
    assert engine.playerlist == (None,)


@pytest.mark.hands(
    [[11, 3], [11, 1]],
    [[11, 3],],
    [[11, 1],],
)
def test_Engine__split(mocker, hands, engine, player):
    """Given a hand that can be split and a player, :meth:`Engine._split`
    should split the hand and update the UI.
    """
    prehand, *posthands = hands
    player.hands = (prehand,)
    assert engine._split(prehand, player)
    assert player.hands == tuple(posthands)
    assert engine.ui.mock_calls == [
        mocker.call.splits(player, 20),
    ]


class EngineTestCase(ut.TestCase):
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
        player.bet = 20
        dhand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)
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
        player.bet = 20
        dhand = cards.Hand([
            cards.Card(1, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)
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
        player.bet = expected / 2.5
        dhand = cards.Hand([
            cards.Card(13, 0),
            cards.Card(12, 3),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)
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
        player.bet = expected / 2.5
        dhand = cards.Hand([
            cards.Card(1, 0),
            cards.Card(6, 3),
            cards.Card(4, 3),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)
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
        player.bet = 20
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)
        g.end()
        actual = player.chips

        self.assertEqual(expected, actual)

    def test_end_player_wins(self):
        """If the player wins, the player gets double their initial
        bet.
        """
        # Expected value.
        expected = 40

        # Test data and state.
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        player.bet = expected // 2
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)

        # Run test.
        g.end()

        # Gather actual.
        actual = player.chips

        # Determine test result.
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
        player.bet = 20

        # This looks a little weird. Shouldn't the hand be different
        # between the first two call.updates() since the cards in the
        # hand will be different at those points?
        #
        # No. game.play() is sending the dealer's hand object to
        # ui.update(), and we are testing to make sure the same
        # hand is sent. Since objects are mutable, the hand has three
        # cards in it when assertEqual() runs, so the expected hand
        # needs to have all three cards, too.
        expected = call(player, player.bet * 2)

        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)
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
        player.bet

        # This looks a little weird. Shouldn't the hand be different
        # between the first two call.updates() since the cards in the
        # hand will be different at those points?
        #
        # No. game.play() is sending the dealer's hand object to
        # ui.update(), and we are testing to make sure the same
        # hand is sent. Since objects are mutable, the hand has three
        # cards in it when assertEqual() runs, so the expected hand
        # needs to have all three cards, too.
        expected = call(player, player.bet)

        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)
        g.end()
        actual = mock_ties_split.mock_calls[-1]

        self.assertEqual(expected, actual)

    @patch('blackjack.game.BaseUI.wins_split')
    def test_end_split_with_ui(self, mock_split):
        """Once the payout is determined, end() should send the event
        to the UI. If the hand is split, that event should be
        'splitpayout' if the hand wins.
        """
        # Set up for expected values.
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
        player.bet = 20

        # Expected values.
        # This looks a little weird. Shouldn't the hand be different
        # between the first two call.updates() since the cards in the
        # hand will be different at those points?
        #
        # No. game.play() is sending the dealer's hand object to
        # ui.update(), and we are testing to make sure the same
        # hand is sent. Since objects are mutable, the hand has three
        # cards in it when assertEqual() runs, so the expected hand
        # needs to have all three cards, too.
        expected = call(player, player.bet * 2)

        # Test data and state.
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)

        # Run test.
        g.end()

        # Gather actuals.
        actual = mock_split.mock_calls[-1]

        # Determine test result.
        self.assertEqual(expected, actual)

    @patch('blackjack.game.BaseUI.tie')
    def test_end_tie_with_ui(self, mock_tie):
        """If the player ties, the player gets back their initial
        bet.
        """
        # Set up for expected values.
        phand = cards.Hand([
            cards.Card(10, 1),
            cards.Card(10, 0),
        ])
        player = players.AutoPlayer((phand,), 'John', 0)
        player.bet = 20

        # Expected values.
        expected = player.bet
        expected_call = call(player, player.bet)

        # Test data and state.
        dhand = cards.Hand([
            cards.Card(10, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)

        # Run test.
        g.end()

        # Gather actuals.
        actual = player.chips
        actual_call = mock_tie.mock_calls[-1]

        # Determine test success.
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
        player.bet = expected // 4
        dhand = cards.Hand([
            cards.Card(7, 3),
            cards.Card(11, 0),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)
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
        player.bet = 20

        # This looks a little weird. Shouldn't the hand be different
        # between the first two call.updates() since the cards in the
        # hand will be different at those points?
        #
        # No. game.play() is sending the dealer's hand object to
        # ui.update(), and we are testing to make sure the same
        # hand is sent. Since objects are mutable, the hand has three
        # cards in it when assertEqual() runs, so the expected hand
        # needs to have all three cards, too.
        expected = call(player, player.bet * 2)

        dhand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(10, 0, cards.DOWN),
        ])
        dealer = players.Dealer((dhand,), 'Dealer', None)
        g = game.Engine(None, dealer, (player,), None, 30)
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

    def test_play_with_insurance(self):
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
        player.bet = expected_insured * 2
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
        exp_attrs = {
            'class': 'Engine',
            'bet_max': 500,
            'bet_min': 20,
            'buyin': 200,
            'card_count': 0,
            'deck': deck.serialize(),
            'deck_cut': False,
            'deck_size': 6,
            'dealer': dealer.serialize(),
            'playerlist': [
                player1.serialize(),
                player2.serialize(),
            ],
            'running_count': False,
            'save_file': 'save.json',
        }
        mock_open().__enter__().read.return_value = json.dumps(exp_attrs)

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
        act_attrs = json.loads(g.serialize())

        self.assertListEqual(exp_open, act_open)
        self.assertListEqual(exp_ui, act_ui)
        self.assertDictEqual(exp_attrs, act_attrs)

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
            'bet_max': 500,
            'bet_min': 20,
            'buyin': 200,
            'card_count': 0,
            'deck': deck.serialize(),
            'deck_cut': False,
            'deck_size': deck.size,
            'dealer': dealer.serialize(),
            'playerlist': [
                player1.serialize(),
                player2.serialize(),
            ],
            'running_count': False,
            'save_file': 'ham',
        }

        g = game.Engine(deck, dealer, (player1, player2,), None, 200, 'ham')
        text = g.serialize()
        act = json.loads(text)

        self.assertDictEqual(exp, act)

    # Test Engine.bet().
    @patch('blackjack.game.BaseUI.joins')
    @patch('blackjack.game.BaseUI.leaves')
    @patch('blackjack.game.make_player')
    def _replace_player_tests(
            self,
            exp_before,
            exp_after,
            exp_call_leaves,
            exp_call_joins,
            new_player,
            engine,
            mock_make,
            mock_leaves,
            mock_joins
    ):
        """Test for bet conditions that cause players to be replaced."""
        # Patch test behavior.
        mock_make.return_value = new_player

        # Run test and get actuals.
        act_before = engine.playerlist[:]
        engine.bet()
        act_after = engine.playerlist[:]
        act_call_leaves = mock_leaves.mock_calls
        act_call_joins = mock_joins.mock_calls

        # Determine test result.
        self.assertTupleEqual(exp_before, act_before)
        self.assertTupleEqual(exp_after, act_after)
        self.assertListEqual(exp_call_leaves, act_call_leaves)
        self.assertListEqual(exp_call_joins, act_call_joins)

    @patch('blackjack.game.BaseUI.bet')
    def test_bet_take_bet(self, mock_bet):
        """Engine.bet() will take the bet from each player in the game,
        tracking the amount with the player."""
        # Expected values.
        exp_chips = [1000, 1500, ]
        exp_bet = 500
        names = ['John', 'Michael', ]
        playerlist = [
            players.AutoPlayer([], name, chips + exp_bet)
            for name, chips in zip(names, exp_chips)
        ]
        exp_call_bet = [
            call(playerlist[0], exp_bet),
            call(playerlist[1], exp_bet),
        ]

        # Test data and state.
        engine = game.Engine(
            playerlist=playerlist,
            bet_min=20,
            bet_max=exp_bet
        )

        # Run test.
        engine.bet()

        # Extract actuals.
        act_chips = [player.chips for player in playerlist]
        act_bets = [player.bet for player in playerlist]
        act_call_bet = mock_bet.mock_calls

        # Determine test result.
        self.assertListEqual(exp_chips, act_chips)
        for act_bet in act_bets:
            self.assertEqual(exp_bet, act_bet)
        self.assertListEqual(exp_call_bet, act_call_bet)

    def test_bet_remove_players_without_enough_chips(self):
        """Engine.bet() will remove players who cannot make the
        minimum bet."""
        # Expected values.
        new_player = players.AutoPlayer([], 'Graham', 1000)
        exp_before = (
            players.AutoPlayer([], 'John', 1000),
            players.AutoPlayer([], 'Michael', 1500),
            players.AutoPlayer([], 'Terry', 10),
        )
        exp_after = (*exp_before[:2], new_player)
        exp_call_leaves = [call(exp_before[2]), ]
        exp_call_joins = [call(new_player), ]

        # Test data and state.
        bet_min = exp_before[-1].chips + 10
        engine = game.Engine(
            playerlist=exp_before,
            bet_min=bet_min
        )

        # Run test and determine result.
        self._replace_player_tests(
            exp_before,
            exp_after,
            exp_call_leaves,
            exp_call_joins,
            new_player,
            engine
        )

    def test_bet_remove_players_below_min_bet(self):
        """Engine.bet() will remove players who bet below the minimum."""
        # Expected values.
        new_player = players.AutoPlayer([], 'Graham', 1000)
        exp_before = (
            players.AutoPlayer([], 'John', 1000),
            players.AutoPlayer([], 'Michael', 1500),
            players.AutoPlayer([], 'Terry', 1000),
        )
        exp_after = (exp_before[0], new_player, exp_before[2])
        exp_call_leaves = [call(exp_before[1]), ]
        exp_call_joins = [call(new_player), ]

        # Test data and state.
        def will_bet_zero(self, _):
            return 0
        exp_before[1].will_bet = MethodType(will_bet_zero, exp_before[1])
        bet_min = 20
        engine = game.Engine(
            playerlist=exp_before,
            bet_min=bet_min
        )

        # Run test and determine result.
        self._replace_player_tests(
            exp_before,
            exp_after,
            exp_call_leaves,
            exp_call_joins,
            new_player,
            engine
        )

    def test_bet_cap_bet_above_maximum(self):
        """Engine.bet() will change bets above the maximum bet to the
        maximum bet."""
        # Expected values.
        bet_max = 100
        playerlist = (
            players.AutoPlayer([], 'John', 1000),
            players.AutoPlayer([], 'Michael', 1500),
            players.AutoPlayer([], 'Terry', 1000),
        )
        exp = [(p.name, bet_max, p.chips) for p in playerlist]

        # Test data and state.
        def will_bet_more(self, _):
            return bet_max + 50
        for player in playerlist:
            player.chips += bet_max
        playerlist[1].will_bet = MethodType(will_bet_more, playerlist[1])
        engine = game.Engine(
            playerlist=playerlist,
            bet_max=bet_max
        )

        # Run test and get actuals.
        engine.bet()
        act = [(p.name, p.bet, p.chips) for p in engine.playerlist]

        # Determine test result.
        self.assertListEqual(exp, act)

    def test_bet_remove_players_cannot_cover_bet(self):
        """Engine.bet() will remove players who bet more chips than
        they have."""
        # Expected values.
        new_player = players.AutoPlayer([], 'Graham', 1000)
        exp_before = (
            players.AutoPlayer([], 'John', 400),
            players.AutoPlayer([], 'Michael', 1500),
            players.AutoPlayer([], 'Terry', 1000),
        )
        exp_after = (new_player, *exp_before[1:])
        exp_call_leaves = [call(exp_before[0]), ]
        exp_call_joins = [call(new_player), ]

        # Test data and state.
        def will_bet_500(self, _):
            return 500
        exp_before[0].will_bet = MethodType(will_bet_500, exp_before[0])
        bet_min = 20
        bet_max = 1000
        engine = game.Engine(
            playerlist=exp_before,
            bet_min=bet_min,
            bet_max=bet_max
        )

        # Run test and determine result.
        self._replace_player_tests(
            exp_before,
            exp_after,
            exp_call_leaves,
            exp_call_joins,
            new_player,
            engine
        )


class SplittingRulesTestCase(ut.TestCase):
    """Unit tests for the splitting rule in blackjack."""
    def setUp(self):
        self.player = players.AutoPlayer(name='John')
        playerlist = [self.player,]
        self.engine = game.Engine(playerlist=playerlist)

    def tearDown(self):
        self.engine = None
        self.player = None

    def test__can_split_if_doubles(self):
        """Given a hand with two cards of the same value and a player
        who will split the hand, Engine._split() will split the hand,
        take the bet from the player, and return True.
        """
        # Expected values.
        expected_hands = (
            cards.Hand([cards.Card(11, 3),]),
            cards.Hand([cards.Card(11, 1),]),
        )
        expected_return = True
        exp_chips = 0

        # Test data and state.
        init_hands = [cards.Hand([
            expected_hands[0][0],
            expected_hands[1][0],
        ]),]
        self.player.bet = 50
        self.player.chips = self.player.bet
        self.player.hands = init_hands

        # Run test and gather actuals.
        actual_return = self.engine._split(init_hands[0], self.player)
        actual_hands = self.player.hands
        act_chips = self.player.chips

        # Determine test results.
        self.assertEqual(expected_hands, actual_hands)
        self.assertEqual(expected_return, actual_return)
        self.assertEqual(exp_chips, act_chips)

    def test__cannot_split_if_not_doubles(self):
        """Given a hand with cards with different values and a player,
        _split() should not split the hand and return false.
        """
        # Expected values.
        expected_h1 = (cards.Hand([
            cards.Card(11, 3),
            cards.Card(2, 1),
        ]),)
        expected_return = False

        # Test data and state.
        self.player.hands = expected_h1

        # Run test and gather actuals.
        actual_return = self.engine._split(expected_h1[0], self.player)
        actual_h1 = self.player.hands

        # Determine test result.
        self.assertEqual(expected_h1, actual_h1)
        self.assertEqual(expected_return, actual_return)

    def test__cannot_split_if_cannot_cover_bet(self):
        """Given a hand with cards with different values and a player
        without enough chips to cover the additional bet, _split()
        should not split the hand and return false.
        """
        # Expected values.
        expected_hands = (cards.Hand([
            cards.Card(11, 3),
            cards.Card(2, 1),
        ]),)
        expected_return = False
        expected_chips = 0

        # Test data and state.
        self.player.bet = expected_chips + 1
        self.player.chips = expected_chips
        self.player.hands = expected_hands[:]

        # Run test and gather actuals.
        actual_return = self.engine._split(expected_hands[0], self.player)
        actual_hands = self.player.hands
        actual_chips = self.player.chips

        # Determine test result.
        self.assertEqual(expected_hands, actual_hands)
        self.assertEqual(expected_return, actual_return)


class mainTestCase(ut.TestCase):
    def setUp(self):
        self.dealer = players.Dealer()
        self.dealer.hands = [
            cards.Hand([
                cards.Card(8, 3),
                cards.Card(12, 1),
            ]),
        ]
        self.playerlist = [
            players.AutoPlayer(name='spam'),
            players.AutoPlayer(name='eggs'),
        ]
        self.save = 'bacon'

    def tearDown(self):
        self.dealer = None
        self.players = None
        self.save = None

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
        # Expected values.
        exp = [
            call(
                dealer=self.dealer,
                playerlist=self.playerlist,
                save_file=self.save
            ),
            call().ui.start(
                is_interactive=True,
                splash_title=game.splash_title
            ),
            call().new_game(),
            call().bet(),
            call().deal(),
            call().play(),
            call().end(),
            call().save(self.save),
            call().ui.nextgame_prompt(),
            call().ui.cleanup(),
            call().ui.nextgame_prompt().value.__bool__(),
            call().bet(),
            call().deal(),
            call().play(),
            call().end(),
            call().save(self.save),
            call().ui.nextgame_prompt(),
        ]

        # Test data and state.
        engine = game.Engine(
            dealer=self.dealer,
            playerlist=self.playerlist,
            save_file=self.save
        )
        engine.dealer = self.dealer
        engine.save_file = self.save

        # Run test.
        loop = game.main(engine)
        result = next(loop)
        result = loop.send(result)
        _ = loop.send(result)

        # Gather actuals.
        act = mock_engine.mock_calls

        # Determine test results.
        self.assertListEqual(exp, act)

    @patch('blackjack.game.Engine')
    def test_call_game_phases_with_dealer_blackjack(self, mock_engine):
        """main() should call each phase of a backjack game in the
        Engine object.
        """
        # Test data and state.
        self.dealer.hands = [
            cards.Hand([
                cards.Card(1, 3, cards.UP),
                cards.Card(12, 1, cards.DOWN),
            ]),
        ]
        engine = game.Engine(
            dealer=self.dealer,
            playerlist=self.playerlist,
            save_file=self.save
        )
        engine.dealer = self.dealer
        engine.save_file = self.save

        # Expected values.
        exp = [
            call(
                dealer=self.dealer,
                playerlist=self.playerlist,
                save_file=self.save
            ),
            call().ui.start(
                is_interactive=True,
                splash_title=game.splash_title
            ),
            call().new_game(),
            call().bet(),
            call().deal(),
            call().ui.flip(self.dealer, self.dealer.hands[0]),
            call().end(),
            call().save(self.save),
            call().ui.nextgame_prompt(),
            call().ui.cleanup(),
            call().ui.nextgame_prompt().value.__bool__(),
            call().bet(),
            call().deal(),
            call().ui.flip(self.dealer, self.dealer.hands[0]),
            call().end(),
            call().save(self.save),
            call().ui.nextgame_prompt(),
        ]
        exp_facing = [cards.UP, cards.UP]

        # Run test.
        loop = game.main(engine)
        result = next(loop)
        result = loop.send(result)
        _ = loop.send(result)

        # Gather actuals.
        act = mock_engine.mock_calls
        act_facing = [c.facing for c in engine.dealer.hands[0]]

        # Determine test results.
        self.assertListEqual(exp, act)
        self.assertListEqual(exp_facing, act_facing)


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
