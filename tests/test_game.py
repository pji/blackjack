"""
test_game.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.game module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import json
from functools import partial
from random import seed
from types import MethodType

import pytest

from blackjack import cards, cli, game, players
from tests.common import deck, engine, hand, hands, player


# Utility functions.
def raises_test(cls, *args, **kwargs):
    """Return the exception raised by the callable."""
    try:
        cls(*args, **kwargs)
    except Exception as ex:
        return type(ex)
    return None


# Common Engine tests.
def engine_end_test(engine, dhands, phands, player):
    """A common test for :meth:`Engine.end`."""
    player.bet = 20
    player.hands = phands
    engine.dealer.hands = dhands
    engine.playerlist = (player,)
    engine.end()


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


def test_Engine_init_all_invalids():
    """Given parameters, the attributes of the :class:`Engine`
    object should be set to given values.
    """
    raises = partial(raises_test, game.Engine)
    assert raises(ui='spam') == ValueError


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
def test_Engine__double_down_blackjack(mocker, engine, hand, player):
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


@pytest.mark.hand([11, 3], [8, 1])
def test_Engine__split_invalid(mocker, hand, engine, player):
    """Given a hand that cannot be split and a player,
    :meth:`Engine._split` should neither split the hand
    nor update the UI.
    """
    player.hands = (hand,)
    assert not engine._split(hand, player)
    assert player.hands == (hand,)
    assert engine.ui.mock_calls == []


@pytest.mark.hand([11, 3], [11, 1])
def test_Engine__split_invalid(mocker, hand, engine, player):
    """Given a hand that cannot be split and a player that cannot
    cover the cost, :meth:`Engine._split` should neither split the
    hand nor update the UI.
    """
    player.bet = 20
    player.chips = 0
    player.hands = (hand,)
    assert not engine._split(hand, player)
    assert player.hands == (hand,)
    assert engine.ui.mock_calls == []


# Tests for Engine public methods.
def test_Engine_bet(mocker, engine, player):
    """:meth:`Engine.bet` will take the bet from each player in the
    game, tracking the amount with the player.
    """
    player2 = players.AutoPlayer(name='Graham', chips=200)
    engine.playerlist = (player, player2,)
    engine.bet_min = 20
    engine.bet_max = 50
    engine.bet()
    assert player.bet == 50
    assert player.chips == 50
    assert player2.bet == 50
    assert player2.chips == 150
    assert engine.ui.mock_calls == [
        mocker.call.bet(player, 50),
        mocker.call.bet(player2, 50),
    ]


def test_Engine_bet_remove_players_without_chips(mocker, engine, player):
    """Engine.bet() will remove players with no chips.
    """
    player2 = players.AutoPlayer(name='Graham', chips=0)
    engine.playerlist = (player, player2,)
    engine.bet_min = 20
    engine.bet_max = 50
    engine.bet()
    assert player.bet == 50
    assert player.chips == 50
    assert player2 not in engine.playerlist
    assert engine.ui.mock_calls == [
        mocker.call.bet(player, 50),
        mocker.call.leaves(player2),
        mocker.call.joins(engine.playerlist[1]),
        mocker.call.bet(engine.playerlist[1], 20),
    ]


def test_Engine_bet_remove_players_below_min_bet(mocker, engine, player):
    """:meth:`Engine.bet` will remove players who bet below the minimum."""
    def will_bet_zero(self, _):
        return 0

    player2 = players.AutoPlayer(name='Graham', chips=200)
    player2.will_bet = MethodType(will_bet_zero, player2)
    engine.playerlist = (player, player2,)
    engine.bet_min = 20
    engine.bet_max = 50
    engine.bet()
    assert player.bet == 50
    assert player.chips == 50
    assert player2 not in engine.playerlist
    assert engine.ui.mock_calls == [
        mocker.call.bet(player, 50),
        mocker.call.leaves(player2),
        mocker.call.joins(engine.playerlist[1]),
        mocker.call.bet(engine.playerlist[1], 20),
    ]


def test_Engine_bet_cap_bet_above_max(mocker, engine, player):
    """:meth:`Engine.bet` will remove players who bet below the minimum."""
    def will_bet_more(self, _):
        return 100

    player2 = players.AutoPlayer(name='Graham', chips=200)
    player2.will_bet = MethodType(will_bet_more, player2)
    engine.playerlist = (player, player2,)
    engine.bet_min = 20
    engine.bet_max = 50
    engine.bet()
    assert player.bet == 50
    assert player.chips == 50
    assert player2.bet == 50
    assert player2.chips == 150
    assert engine.ui.mock_calls == [
        mocker.call.bet(player, 50),
        mocker.call.bet(player2, 50),
    ]


def test_Engine_bet_remove_players_cannot_cover(mocker, engine, player):
    """Engine.bet() will remove players who cannot make the
    minimum bet.
    """
    player2 = players.AutoPlayer(name='Graham', chips=10)
    engine.playerlist = (player, player2,)
    engine.bet_min = 20
    engine.bet_max = 50
    engine.bet()
    assert player.bet == 50
    assert player.chips == 50
    assert player2 not in engine.playerlist
    assert engine.ui.mock_calls == [
        mocker.call.bet(player, 50),
        mocker.call.leaves(player2),
        mocker.call.joins(engine.playerlist[1]),
        mocker.call.bet(engine.playerlist[1], 20),
    ]


@pytest.mark.deck([11, 3, False], [1, 3, False])
@pytest.mark.hand([1, 3, True], [11, 3, False])
def test_Engine_deal(mocker, deck, engine, hand):
    """In a :class:`Engine` object with a deck and a dealer,
    :meth:`Engine.deal` should deal an initial hand of blackjack
    to the dealer from the deck.
    """
    engine.deck = deck
    engine.deal()
    assert engine.dealer.hands == (hand,)
    assert engine.ui.mock_calls == [
        mocker.call.deal(engine.dealer, hand)
    ]


@pytest.mark.deck([11, 3, False], [1, 3, False], [4, 2, False], [7, 1, False])
@pytest.mark.hands(
    [[7, 1, True], [1, 3, False]],
    [[4, 2, True], [11, 3, False]]
)
def test_Engine_deal_with_players(deck, hands, engine, player):
    """In a :class:`Engine` object with a deck, dealer, and player
    in the playerlist, :meth:`Engine.deal` should deal an initial
    hand of blackjack to the dealer and the player from the deck.
    """
    phand, dhand = hands
    engine.deck = deck
    engine.playerlist = (player,)
    engine.deal()
    assert engine.dealer.hands == (dhand,)
    assert player.hands == (phand,)


@pytest.mark.hands(
    [[11, 3], [1, 3]],
    [[12, 2], [7, 1], [4, 1]],
)
def test_Engine_end_dealer_blackjack_player_21(engine, hands, player):
    """Given a dealer hand that is a blackjack, all players who
    don't have blackjack lose.
    """
    dhand, phand = hands
    engine_end_test(engine, (dhand,), (phand,), player)
    assert player.chips == 100


@pytest.mark.hands(
    [[11, 3], [1, 3]],
    [[5, 2], [7, 1], [4, 1]],
    [[5, 0], [3, 3], [6, 0]],
)
def test_Engine_end_dealer_blackjack_player_split_21(engine, hands, player):
    """Given a dealer hand that is a blackjack, all players who
    don't have blackjack lose, including those with split hands.
    """
    dhand, *phands = hands
    engine_end_test(engine, (dhand,), phands, player)
    assert player.chips == 100


@pytest.mark.hands(
    [[12, 2], [7, 1]],
    [[11, 3], [1, 3]],
)
def test_Engine_end_player_blackjack(engine, hands, player):
    """If the player wins with a blackjack, they get two and a
    half times their initial bet back.
    """
    dhand, phand = hands
    engine_end_test(engine, (dhand,), (phand,), player)
    assert player.chips == 150


@pytest.mark.hands(
    [[12, 2], [6, 1], [5, 3]],
    [[11, 3], [1, 3]],
)
def test_Engine_end_player_blackjack_dealer_21(engine, hands, player):
    """If the player wins with a blackjack while the dealer has 21,
    they get two and a half times their initial bet back.
    """
    dhand, phand = hands
    engine_end_test(engine, (dhand,), (phand,), player)
    assert player.chips == 150


@pytest.mark.hands(
    [[7, 2], [11, 1]],
    [[4, 3], [6, 3], [10, 0]],
)
def test_Engine_end_player_double_down(mocker, engine, hands, player):
    """If the hand was doubled down, the pay out should quadruple
    the initial bet.
    """
    dhand, phand = hands
    phand.doubled_down = True
    engine_end_test(engine, (dhand,), (phand,), player)
    assert player.chips == 180
    assert engine.ui.mock_calls == [
        mocker.call.wins(player, player.bet * 4),
    ]


@pytest.mark.hands(
    [[1, 2], [11, 1]],
    [[4, 3], [6, 3], [10, 0]],
)
def test_Engine_end_player_insured(mocker, engine, hands, player):
    """If the player was insured and the dealer had a blackjack,
    the insurance pay out should double the insurance amount.
    """
    dhand, phand = hands
    player.insured = 10
    engine_end_test(engine, (dhand,), (phand,), player)
    assert player.chips == 120
    assert engine.ui.mock_calls == [
        mocker.call.insurepay(player, player.insured * 2),
        mocker.call.loses(player),
    ]


@pytest.mark.hands(
    [[12, 2], [7, 1]],
    [[11, 3], [5, 3]],
)
def test_Engine_end_player_loses(mocker, engine, hands, player):
    """If the player loses, the player loses their initial bet."""
    dhand, phand = hands
    engine_end_test(engine, (dhand,), (phand,), player)
    assert player.chips == 100
    assert engine.ui.mock_calls == [
        mocker.call.loses(player),
    ]


@pytest.mark.hands(
    [[12, 2], [7, 1]],
    [[1, 3], [4, 3], [9, 0]],
    [[1, 3], [11, 3]],
)
def test_Engine_end_player_split_not_blackjack(mocker, engine, hands, player):
    """If the hand was split from aces it cannot be counted as
    a blackjack.
    """
    dhand, *phands = hands
    engine_end_test(engine, (dhand,), phands, player)
    assert player.chips == 140
    assert engine.ui.mock_calls == [
        mocker.call.loses(player),
        mocker.call.wins_split(player, player.bet * 2),
    ]


@pytest.mark.hands(
    [[12, 2], [7, 1]],
    [[1, 3], [11, 3]],
    [[1, 3], [4, 3], [9, 0]],
)
def test_Engine_end_player_split_lost(mocker, engine, hands, player):
    """If the hand was split from aces it cannot be counted as
    a blackjack. If it was the split hand that lost, the UI call
    should include a call to :meth:`Engine.ui.loses_split`.
    """
    dhand, *phands = hands
    engine_end_test(engine, (dhand,), phands, player)
    assert player.chips == 140
    assert engine.ui.mock_calls == [
        mocker.call.wins(player, player.bet * 2),
        mocker.call.loses_split(player),
    ]


@pytest.mark.hands(
    [[12, 2], [7, 1]],
    [[1, 3], [11, 3]],
    [[1, 3], [7, 3], [9, 0]],
)
def test_Engine_end_player_split_ties(mocker, engine, hands, player):
    """If the hand was split from aces it cannot be counted as
    a blackjack. If the split hand ties, the UI call should include
    a call to :meth:`Engine.ui.ties_split`.
    """
    dhand, *phands = hands
    engine_end_test(engine, (dhand,), phands, player)
    assert player.chips == 160
    assert engine.ui.mock_calls == [
        mocker.call.wins(player, player.bet * 2),
        mocker.call.ties_split(player, player.bet),
    ]


@pytest.mark.hands(
    [[12, 2], [7, 1]],
    [[11, 3], [7, 3]],
)
def test_Engine_end_player_ties(mocker, engine, hands, player):
    """If the player ties, the player gets back their initial bet."""
    dhand, phand = hands
    engine_end_test(engine, (dhand,), (phand,), player)
    assert player.chips == 120
    assert engine.ui.mock_calls == [
        mocker.call.tie(player, player.bet)
    ]


@pytest.mark.hands(
    [[12, 2], [7, 1]],
    [[11, 3], [10, 3]],
)
def test_Engine_end_player_wins(mocker, engine, hands, player):
    """If the player wins, the player gets double their initial
    bet.
    """
    dhand, phand = hands
    engine_end_test(engine, (dhand,), (phand,), player)
    assert player.chips == 140
    assert engine.ui.mock_calls == [
        mocker.call.wins(player, player.bet * 2),
    ]


def test_Engine_new_game_players_join(mocker, engine, player):
    """When players join a game, :meth:`Engine.new_game` should send
    a join event to the UI for each player in the game.
    """
    engine.playerlist = (player,)
    engine.new_game()
    assert engine.ui.mock_calls == [
        mocker.call.joins(engine.dealer),
        mocker.call.joins(player),
    ]


@pytest.mark.deck([11, 3], [5, 1], [6, 0])
@pytest.mark.hands(
    [[2, 1], [3, 2]],
    [[2, 1], [3, 2], [6, 0], [5, 1], [11, 3]]
)
def test_Engine_play_dealer_bust(deck, engine, hands):
    """In a Engine object with a deck and a dealer with a dealt
    hand, play() should deal cards to the dealer until the dealer
    stands on a bust.
    """
    dhand, expected = hands
    engine.deck = deck
    engine.dealer.hands = (dhand,)
    engine.play()
    assert dhand == expected


@pytest.mark.deck([10, 1])
@pytest.mark.hands(
    [[7, 0], [3, 2, False]],
    [[7, 0], [3, 2], [10, 1]]
)
def test_Engine_play_dealer_17(mocker, deck, engine, hands):
    """In a Engine object with a deck and a dealer, play() should
    deal cards to the dealer until the dealer stands on a score of
    17 or more.
    """
    dhand, expected = hands
    engine.deck = deck
    engine.dealer.hands = (dhand,)
    engine.play()
    assert dhand == expected
    assert engine.ui.mock_calls == [
        mocker.call.flip(engine.dealer, dhand),
        mocker.call.hit(engine.dealer, dhand),
        mocker.call.stand(engine.dealer, dhand),
    ]


@pytest.mark.deck([11, 0], [11, 3])
@pytest.mark.hands(
    [[5, 0], [5, 1]],
    [[5, 2], [4, 3]],
    [[5, 0], [5, 1], [11, 0]],
    [[5, 2], [4, 3], [11, 3]],
)
def test_Engine_play_with_player(deck, engine, hands, player):
    """In a Engine with a deck, dealer with a hand, and a player
    with a hand, play a round of blackjack.
    """
    dhand, phand, dexpected, pexpected = hands
    engine.deck = deck
    engine.dealer.hands = (dhand,)
    player.hands = (phand,)
    engine.playerlist = (player,)
    engine.play()
    assert dhand == dexpected
    assert phand == pexpected


@pytest.mark.deck([11, 0, False])
@pytest.mark.hands(
    [[10, 0], [10, 1]],
    [[4, 2], [6, 3]],
    [[4, 2], [6, 3], [11, 0]],
)
def test_Engine_play_with_player_double_down(deck, engine, hands, player):
    """Given a hand with a value from 9 to 11 and a player who
    will double down, :meth:`Engine.play` should hit the hand
    once and stand.
    """
    dhand, phand, expected = hands
    engine.deck = deck
    engine.dealer.hands = (dhand,)
    player.hands = (phand,)
    engine.playerlist = (player,)
    engine.play()
    assert phand == expected
    assert phand.doubled_down


@pytest.mark.deck([1, 3], [9, 3], [2, 2])
@pytest.mark.hands(
    [[10, 0], [10, 1]],
    [[11, 0], [11, 3]],
    [[11, 0], [2, 2], [9, 3]],
    [[11, 3], [1, 3]],
)
def test_Engine_play_with_player_split(deck, engine, hands, player):
    """If given a hand that can be split and a player who will
    split that hand, :meth:`Engine.play` should handle both of
    the hands.
    """
    dhand, phand, *expected = hands
    engine.deck = deck
    engine.dealer.hands = (dhand,)
    player.hands = (phand,)
    engine.playerlist = (player,)
    engine.play()
    assert player.hands == tuple(expected)


@pytest.mark.deck([1, 3], [2, 2])
@pytest.mark.hands(
    [[10, 0], [10, 1]],
    [[1, 0], [1, 3]],
    [[1, 0], [2, 2]],
    [[1, 3], [1, 3]],
)
def test_Engine_play_with_player_split_aces(deck, engine, hands, player):
    """Given a hand with two aces and a player who will split that
    hand, :meth:`Engine.play` should split the hand and hit each of
    the split hands only once before standing.
    """
    dhand, phand, *expected = hands
    engine.deck = deck
    engine.dealer.hands = (dhand,)
    player.hands = (phand,)
    engine.playerlist = (player,)
    engine.play()
    assert player.hands == tuple(expected)


@pytest.mark.deck([8, 1], [11, 0])
@pytest.mark.hands(
    [[1, 0], [10, 1, False]],
    [[4, 2], [6, 3]],
    [[4, 2], [6, 3], [11, 0]],
)
def test_Engine_play_with_player_insurance(deck, engine, hands, player):
    """Given a dealer hand with an ace showing an a player who
    will insure, :meth:`Engine.play` should insure the player
    then play the round as usual.
    """
    dhand, phand, expected = hands
    engine.deck = deck
    engine.dealer.hands = (dhand,)
    player.bet = 20
    player.hands = (phand,)
    engine.playerlist = (player,)
    engine.play()
    assert phand == expected
    assert player.insured == 10


def test_Engine_restore(engine):
    """When called, :meth:`Engine.restore` should load the serialized
    instance of Engine from file, set the current object's attributes
    to those of the serialized object, and reset the UI.
    """
    path = 'tests/data/savefile'
    with open(path) as fh:
        expected = json.load(fh)
    engine.restore(path)
    actual = json.loads(engine.serialize())
    assert actual == expected


def test_Engine_save(tmp_path, engine):
    """When called, save() should serialize the Engine object and
    write it to a file.
    """
    path = tmp_path / '_test_Engine_save.json'
    expected = engine.serialize()
    engine.save(path)
    with open(path) as fh:
        actual = fh.read()
    assert actual == expected


def test_Engine_serialize(engine):
    """When called, serialize should return the object
    serialized as a JSON string.
    """
    deck = cards.Deck.build(6)
    engine.deck = deck
    serial = engine.serialize()
    assert json.loads(serial) == {
        'class': 'Engine',
        'bet_max': 100,
        'bet_min': 20,
        'buyin': 20,
        'card_count': 0,
        'deck': deck.serialize(),
        'deck_cut': False,
        'deck_size': 6,
        'dealer': players.Dealer(name='Dealer').serialize(),
        'playerlist': [],
        'running_count': False,
        'save_file': 'save.json',
    }


# Tests for main.
@pytest.mark.hand([8, 3], [12, 1])
def test_main_call_game_phases(mocker, hand, player):
    """:func:`main` should call each phase of a backjack game in the
    Engine object.
    """
    mock_engine = mocker.patch('blackjack.game.Engine')
    dealer = players.Dealer(hands=(hand,))
    playerlist = (player,)
    save_path = 'spam'
    engine = game.Engine()
    engine.dealer = dealer
    engine.playerlist = playerlist
    engine.save_file = save_path

    loop = game.main(engine)
    result = next(loop)
    result = loop.send(result)
    _ = loop.send(result)

    assert engine.mock_calls == [
        mocker.call.ui.start(
            is_interactive=True,
            splash_title=game.splash_title
        ),
        mocker.call.new_game(),
        mocker.call.bet(),
        mocker.call.deal(),
        mocker.call.play(),
        mocker.call.end(),
        mocker.call.save(save_path),
        mocker.call.ui.nextgame_prompt(),
        mocker.call.ui.cleanup(),
        mocker.call.ui.nextgame_prompt().value.__bool__(),
        mocker.call.bet(),
        mocker.call.deal(),
        mocker.call.play(),
        mocker.call.end(),
        mocker.call.save(save_path),
        mocker.call.ui.nextgame_prompt(),
    ]


@pytest.mark.hand([1, 3], [12, 1])
def test_main_call_game_phases(mocker, hand, player):
    """:func:`main` should call each phase of a backjack game in the
    Engine object.
    """
    mock_engine = mocker.patch('blackjack.game.Engine')
    dealer = players.Dealer(hands=(hand,))
    playerlist = (player,)
    save_path = 'spam'
    engine = game.Engine()
    engine.dealer = dealer
    engine.playerlist = playerlist
    engine.save_file = save_path

    loop = game.main(engine)
    result = next(loop)
    result = loop.send(result)
    _ = loop.send(result)

    assert engine.mock_calls == [
        mocker.call.ui.start(
            is_interactive=True,
            splash_title=game.splash_title
        ),
        mocker.call.new_game(),
        mocker.call.bet(),
        mocker.call.deal(),
        mocker.call.ui.flip(dealer, hand),
        mocker.call.end(),
        mocker.call.save(save_path),
        mocker.call.ui.nextgame_prompt(),
        mocker.call.ui.cleanup(),
        mocker.call.ui.nextgame_prompt().value.__bool__(),
        mocker.call.bet(),
        mocker.call.deal(),
        mocker.call.ui.flip(dealer, hand),
        mocker.call.end(),
        mocker.call.save(save_path),
        mocker.call.ui.nextgame_prompt(),
    ]
