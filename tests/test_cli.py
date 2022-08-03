"""
test_cli.py
~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.cli module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from contextlib import contextmanager
from io import StringIO
from json import load, loads
import sys
import unittest as ut
from unittest.mock import patch, call, MagicMock

from blessed import Terminal

from blackjack import cards, cli, game, model, players, termui


# Utility functions.
@contextmanager
def capture():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def mock_run_terminal_only_yesno():
    values = [None, model.IsYes(True)]
    for value in values:
        yield value


# Tests.
class LogUITestCase(ut.TestCase):
    tmp = '{:<15} {:<15} {:<}\n'

    # Test start().
    def test_start(self):
        """start() should print the headers for the game output."""
        lines = [
            '\n',
            'BLACKJACK!\n',
            '\n',
            self.tmp.format('Player', 'Action', 'Hand'),
            '\u2500' * 50 + '\n',
        ]
        exp = ''.join(lines)

        with capture() as (out, err):
            ui = cli.LogUI(True)
            ui.start()
        act = out.getvalue()

        self.assertEqual(exp, act)

    # Test end(),
    def test_end(self):
        """end() should print the footers for the game output."""
        lines = [
            '\u2500' * 50 + '\n',
            '\n',
        ]
        exp = ''.join(lines)

        with capture() as (out, err):
            ui = cli.LogUI(False)
            ui.end(True)
        act = out.getvalue()

        self.assertEqual(exp, act)

    # Test _update_bet().
    def test__update_bet(self):
        """Given a player, a bet, and an event, _update_bet() should
        inform the player of the event.
        """
        player = players.Player(name='spam', chips=200)
        bet = 20
        event = 'Bet.'
        fmt = f'{bet} ({player.chips})'
        exp = self.tmp.format(player, event, fmt)

        ui = cli.LogUI()
        with capture() as (out, err):
            ui._update_bet(player, bet, event)
        act = out.getvalue()

        self.assertEqual(exp, act)

    @patch('blackjack.cli.LogUI._update_bet')
    def test_bet_updates(self, mock_update):
        """The methods tested should send _update_bet a player,
        a bet, and event text for display to the user.
        """
        player = players.Player(name='spam')
        bet = 20
        events = [
            'Bet.',
            'Double down.',
            'Insures.',
            'Insure pay.',
            'Tie.',
            'Tie.',
            'Wins.',
            'Wins.',
            'Splits.',
        ]
        exp = [call(player, bet, event) for event in events]
        exp.append(call(player, '', 'Loses.'))
        exp.append(call(player, '', 'Loses.'))

        ui = cli.LogUI()
        ui.bet(player, bet)
        ui.doubledown(player, bet)
        ui.insures(player, bet)
        ui.insurepay(player, bet)
        ui.tie(player, bet)
        ui.ties_split(player, bet)
        ui.wins(player, bet)
        ui.wins_split(player, bet)
        ui.splits(player, bet)
        ui.loses(player)
        ui.loses_split(player)
        act = mock_update.mock_calls

        self.assertListEqual(exp, act)

    # Test _update_event().
    def test__update_event(self):
        """Given a player and an event, _update_event() should
        report that event to the user.
        """
        player = players.Player(name='spam')
        event = 'Joins.'
        exp = self.tmp.format(player, event, '')

        ui = cli.LogUI()
        with capture() as (out, err):
            ui._update_event(player, event)
        act = out.getvalue()

        self.assertEqual(exp, act)

    @patch('blackjack.cli.LogUI._update_event')
    def test_hand_event(self, mock_update):
        """The methods tested should send _update_event a player,
        an event, and optional details to display to the user.
        """
        player = players.Player(name='spam')
        hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 0),
        ])
        events = [
            'Joins.',
            'Leaves.',
            'Shuffles.',
        ]
        exp = [call(player, event) for event in events]

        ui = cli.LogUI()
        ui.joins(player)
        ui.leaves(player)
        ui.shuffles(player)
        act = mock_update.mock_calls

        self.assertListEqual(exp, act)

    # Test _update_hand().
    def test__update_hand(self):
        """Given a player, hand, and an event, _update_hand should
        report that update to the user.
        """
        player = players.Player(name='spam')
        hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 0),
        ])
        event = 'Hand dealt.'
        exp = self.tmp.format(player, event, hand)

        ui = cli.LogUI()
        with capture() as (out, err):
            ui._update_hand(player, hand, event)
        act = out.getvalue()

        self.assertEqual(exp, act)

    @patch('blackjack.cli.LogUI._update_hand')
    def test_hand_updates(self, mock_update):
        """The methods tested should send _update_hand a player,
        hand, and event text for display to the user.
        """
        player = players.Player(name='spam')
        hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 0),
        ])
        events = [
            'Dealt hand.',
            'Flip.',
            'Hit.',
            'Stand.',
        ]
        exp = [call(player, hand, event) for event in events]

        ui = cli.LogUI()
        ui.deal(player, hand)
        ui.flip(player, hand)
        ui.hit(player, hand)
        ui.stand(player, hand)
        act = mock_update.mock_calls

        self.assertListEqual(exp, act)

    # Test cleanup()
    def test_cleanup(self):
        """When called, cleanup() should print the footer and the
        header to the UI.
        """
        lines = [
            '\u2500' * 50 + '\n',
            '\n',
            '\n',
            'BLACKJACK!\n',
            '\n',
            self.tmp.format('Player', 'Action', 'Hand'),
            '\u2500' * 50 + '\n',
        ]
        exp = ''.join(lines)

        with capture() as (out, err):
            ui = cli.LogUI(True)
            ui.cleanup()
        act = out.getvalue()

        self.assertEqual(exp, act)

    # Test _update_status.
    def test__update_status(self):
        """Given an event, _update_status() should report that event
        to the user.
        """
        label = 'Card count:'
        event = '5'
        exp = self.tmp.format(label, '', event)

        ui = cli.LogUI()
        with capture() as (out, err):
            ui._update_status(label, event)
        act = out.getvalue()

        self.assertEqual(exp, act)

    # Test card counting.
    @patch('blackjack.cli.LogUI._update_status')
    def test_update_count(self, mock_update):
        """When an update_card event is received, a message should be
        displayed that shows the new card count.
        """
        # Expected values.
        label = 'Running count:'
        value = '10'
        exp = [call(label, value)]

        # Test data and state.
        ui = cli.LogUI()

        # Run test.
        ui.update_count(value)

        # Gather actual.
        act = mock_update.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    # Test _yesno_prompt().
    @patch('blackjack.cli.input')
    def test_yesno_prompt(self, mock_input):
        """Given a prompt and a default value, prompt the use for a
        yes/no answer and return the result.
        """
        exp_resp = model.IsYes('y')
        exp_call = call('spam [yn] > ')

        mock_input.return_value = 'y'
        ui = cli.LogUI()
        act_resp = ui._yesno_prompt('spam', 'y')
        act_call = mock_input.mock_calls[-1]

        self.assertEqual(exp_resp.value, act_resp.value)
        self.assertEqual(exp_call, act_call)

    @patch('blackjack.cli.LogUI._yesno_prompt')
    def test_prompt_yesnos(self, mock_input):
        """The input methods that ask yes/no questions should call
        _yesno_prompt() with a prompt and a default, and they should
        return the response from _yesno_prompt().
        """
        prompts = [
            'Double down?',
            'Hit?',
            'Insure?',
            'Next game?',
            'Split?',
        ]
        exp_resp = [model.IsYes('n') for _ in range(len(prompts))]
        exp_calls = [call(prompt, 'y') for prompt in prompts]

        mock_input.return_value = model.IsYes('n')
        ui = cli.LogUI()
        act_resp = []
        act_resp.append(ui.doubledown_prompt())
        act_resp.append(ui.hit_prompt())
        act_resp.append(ui.insure_prompt())
        act_resp.append(ui.nextgame_prompt())
        act_resp.append(ui.split_prompt())
        act_calls = mock_input.mock_calls

        self.assertListEqual(exp_calls, act_calls)
        self.assertListEqual(exp_resp, act_resp)


class ParseCliTestCase(ut.TestCase):
    def setUp(self):
        self.original_args = sys.argv

    def tearDown(self):
        sys.argv = self.original_args

    def test_default_game(self):
        """When passed no options, blackjack should start a default
        game with four computer players and a human player.
        """
        # Expected values.
        exp = {
            'table_seats': 6,
            'deck_len': 52 * 6,
            'dealer': players.Dealer(name='Dealer'),
            'playerlist_len': 5,
            'last_player': players.UserPlayer(name='You', chips=200),
            'buyin': 20,
            'save_file': 'save.json',
            'deck_size': 6,
            'deck_cut': False,
        }

        # Test data and state.
        sys.argv = ['python -m blackjack', ]

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act = {
            'table_seats': engine.ui.seats,
            'deck_len': len(engine.deck),
            'dealer': engine.dealer,
            'playerlist_len': len(engine.playerlist),
            'last_player': engine.playerlist[-1],
            'buyin': engine.buyin,
            'save_file': engine.save_file,
            'deck_size': engine.deck_size,
            'deck_cut': engine.deck_cut,
        }

        # Determine test result.
        self.assertDictEqual(exp, act)

    def test_change_buyin(self):
        """When passed the -b option, change amount of chips needed to
        buy into each hand.
        """
        # Expected values.
        exp = 100

        # Test data and state.
        sys.argv = ['python -m blackjack', f'-b {exp}']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act = engine.buyin

        # Determine test result.
        self.assertEqual(exp, act)

    def test_change_chips(self):
        """When passed the -c option, change amount of chips given to
        the user player.
        """
        # Expected values.
        exp = 100

        # Test data and state.
        sys.argv = ['python -m blackjack', f'-c {exp}']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act = engine.playerlist[-1].chips

        # Determine test result.
        self.assertEqual(exp, act)

    @patch('blackjack.cards.randrange', return_value=65)
    def test_cut_deck(self, mock_randrange):
        """When passed the -C option, cut a random number of cards
        between 60 and 75 from the bottom of the deck to make card
        counting harder.
        """
        # Expected values.
        cards_in_deck = 52
        num_decks = 6
        cut_cards = mock_randrange()
        exp = cards_in_deck * num_decks - cut_cards

        # Test data and state.
        sys.argv = ['python -m blackjack', f'-C']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act = len(engine.deck)

        # Determine test result.
        self.assertEqual(exp, act)

    def test_change_decks(self):
        """When passed the -d option, change the number of standard
        decks used to build the deck for the game..
        """
        # Expected values.
        decks = 4
        exp = decks * 52

        # Test data and state.
        sys.argv = ['python -m blackjack', f'-d {decks}']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act = len(engine.deck)

        # Determine test result.
        self.assertEqual(exp, act)

    def test_change_number_of_computer_players(self):
        """When passed the -p option, change the number of computer
        players in the game.
        """
        # Expected values.
        num_players = 7
        exp_seats = num_players + 2
        exp_playerlist_len = num_players + 1

        # Test data and state.
        sys.argv = ['python -m blackjack', f'-p {num_players}']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act_seats = engine.ui.seats
        act_playerlist_len = len(engine.playerlist)

        # Determine test result.
        self.assertEqual(exp_seats, act_seats)
        self.assertEqual(exp_playerlist_len, act_playerlist_len)

    def test_change_save_file(self):
        """When passed the -b option, change amount of chips needed to
        buy into each hand.
        """
        # Expected values.
        exp = 'spam'

        # Test data and state.
        sys.argv = ['python -m blackjack', f'-s {exp}']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act = engine.save_file

        # Determine test result.
        self.assertEqual(exp, act)

    def test_count_cards(self):
        """When passed the -K option, display the running count in the
        UI.
        """
        # Expected values.
        exp = True

        # Test data and state.
        sys.argv = ['python -m blackjack', f'-K']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act = engine.running_count

        # Determine test result.
        self.assertEqual(exp, act)

    def test_no_user_player(self):
        """When passed the -a option, do not add a user player to
        the game.
        """
        # Expected values.
        not_exp = players.UserPlayer

        # Test data and state.
        sys.argv = ['python -m blackjack', f'-a']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act = type(engine.playerlist[-1])

        # Determine test result.
        self.assertNotIsInstance(act, not_exp)

    def test_restore_from_file(self):
        """When passed a -f option followed by a file path, create a
        new game from the save information stored in the file.
        """
        # Set up for expected value.
        path = 'tests/data/savefile'
        with open(path) as fp:

            # Expected values.
            exp = load(fp)

        # Test data and state.
        sys.argv = ['python -m blackjack', '-f tests/data/savefile']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        serial = engine.serialize()
        act = loads(serial)

        # Determine test result.
        for key in act:
            self.assertEqual(exp[key], act[key])
        self.assertDictEqual(exp, act)

    def test_use_logui(self):
        """When passed the -L option, change the UI to use LogUI
        instead of TableUI.
        """
        # Expected values.
        exp = cli.LogUI

        # Test data and state.
        sys.argv = ['python -m blackjack', f'-L']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act = engine.ui

        # Determine test result.
        self.assertIsInstance(act, exp)


class TableUITestCase(ut.TestCase):
    def test_subclass(self):
        """TableUI is a subclass of game.EngineUI."""
        exp = game.EngineUI
        act = cli.TableUI
        self.assertTrue(issubclass(act, exp))

    # General operations methods.
    def test_init_optional_attrs(self):
        """On initialization, TableUI should accept optional
        attributes.
        """
        fields = [
            ['Name', '{:<10}',],
            ['Value', '{:<10}',],
        ]
        ctlr = termui.Table('spam', fields)
        exp = {
            'ctlr': ctlr,
            'seats': 6,
        }

        ui = cli.TableUI(**exp)
        for attr in exp:
            act = getattr(ui, attr)

            self.assertEqual(exp[attr], act)

    def test_init_no_optional_attrs(self):
        """On initialization, TableUI should not require optional
        attributes.
        """
        exp = termui.Table

        ui = cli.TableUI()
        act = ui.ctlr

        self.assertTrue(isinstance(act, exp))

    @patch('blackjack.termui.main')
    def test_end(self, mock_main):
        """end() should terminate UI loop gracefully."""
        exp = call().close()

        ui = cli.TableUI()
        ui.start()
        ui.end()
        act = mock_main.mock_calls[-1]

        self.assertEqual(exp, act)

    @patch('blackjack.termui.main')
    def test_reset(self, mock_main):
        """When called, reset() should terminate the existing
        controller, create a new one, and prime it.
        """
        ui = cli.TableUI()
        ui.start()
        ui.reset()
        reset_ctlr = ui.ctlr
        exp = [
            call().close(),
            call(reset_ctlr, False),
            call().__next__(),
            call().send(('draw',)),
        ]

        act = mock_main.mock_calls[-4:]
        ui.end()

        self.assertListEqual(exp, act)

    @patch('blackjack.termui.main')
    def test_start(self, mock_main):
        """start() should kick off the main loop of the UI, set it
        as the loop attribute, and prime it.
        """
        ui = cli.TableUI()
        term = ui.ctlr
        exp = [
            call(ui.ctlr, False),
            call().__next__(),
            call().send(('draw',))
        ]

        ui.start()
        act = mock_main.mock_calls

        self.assertEqual(exp, act)

    # Update method tests.
    @patch('blackjack.termui.main')
    def test__update_bet(self, mock_main):
        """_update_bet should send an event to the UI loop that a
        player's bet has changed and needs to be updated. The data
        sent in that event should be a copy of the table in the
        termui.Table object.
        """
        player = players.Player(name='spam', chips=80)
        msg = 'Bets.'
        new_data = [[player, 80, 20, '', msg],]
        exp = call().send(('update', new_data))

        unexp_data = [[player, 100, '', '', ''],]
        ui = cli.TableUI()
        ui.ctlr.data = unexp_data
        ui.start()
        ui._update_bet(player, 20, msg)
        act = mock_main.mock_calls[-1]
        ui.end()

        self.assertEqual(exp, act)

        # Since termui.Table determines what fields to update based
        # on differences between it's data table and the data table
        # it's sent, it's very important that the changes made to
        # the data table output by _update_bet() are not yet seen in
        # the data table held by termui.Table.
        #
        # If this test fails, it's likely because you aren't copying
        # the rows of self.ctrl.data. You are referencing them.
        self.assertNotEqual(unexp_data[0][1], 80)

    @patch('blackjack.termui.main')
    def test__update_event(self, mock_main):
        """_update_event should send an event to the UI loop that a
        player has had an event occur. The data sent in that event
        should be a copy of the table in the termui.Table object.
        """
        player = players.Player(name='spam', chips=80)
        msg = 'Walks away.'
        new_data = [[player, 80, '', '', msg],]
        exp = call().send(('update', new_data))

        unexp_data = [[player, 80, '', '', ''],]
        ui = cli.TableUI()
        ui.ctlr.data = unexp_data
        ui.start()
        ui._update_event(player, msg)
        act = mock_main.mock_calls[-1]
        ui.end()

        self.assertEqual(exp, act)

        # Since termui.Table determines what fields to update based
        # on differences between it's data table and the data table
        # it's sent, it's very important that the changes made to
        # the data table output by _update_bet() are not yet seen in
        # the data table held by termui.Table.
        #
        # If this test fails, it's likely because you aren't copying
        # the rows of self.ctrl.data. You are referencing them.
        self.assertNotEqual(unexp_data[0][4], 'Takes hand.')

    @patch('blackjack.termui.main')
    def test__update_hand(self, mock_main):
        """_update_bet should send an event to the UI loop that a
        player's hand has changed and needs to be updated. The data
        sent in that event should be a copy of the table in the
        termui.Table object.
        """
        hand = cards.Hand((
            cards.Card(11, 0),
            cards.Card(5, 2),
        ))
        player = players.Player(name='spam', chips=80)
        msg = 'Takes hand.'
        new_data = [[player, 80, 20, str(hand), msg],]
        exp = call().send(('update', new_data))

        unexp_data = [[player, 80, 20, '', 'Bets.'],]
        ui = cli.TableUI()
        ui.ctlr.data = unexp_data
        ui.start()
        ui._update_hand(player, hand, msg)
        act = mock_main.mock_calls[-1]
        ui.end()

        self.assertEqual(exp, act)

        # Since termui.Table determines what fields to update based
        # on differences between it's data table and the data table
        # it's sent, it's very important that the changes made to
        # the data table output by _update_bet() are not yet seen in
        # the data table held by termui.Table.
        #
        # If this test fails, it's likely because you aren't copying
        # the rows of self.ctrl.data. You are referencing them.
        self.assertNotEqual(unexp_data[0][4], 'Takes hand.')

    @patch('blackjack.termui.print')
    @patch('blackjack.cli.TableUI._update_bet')
    def test_bet_updates(self, mock_update_bet, _):
        """The tested methods should call the _update_bet() method
        with the player, bet, and event text.
        """
        player = players.Player(name='spam', chips=100)
        bet = 20
        exp = [
            call(player, bet, 'Bets.'),
            call(player, bet, 'Doubles down.'),
            call(player, bet, f'Buys {bet} insurance.'),
            call(player, bet, f'Insurance pays {bet}.'),
            call(player, '', 'Loses.'),
            call(player, '', 'Loses.', True),
            call(player, '', f'Ties {bet}.'),
            call(player, '', f'Wins {bet}.'),
            call(player, '', f'Ties {bet}.', True),
            call(player, '', f'Wins {bet}.', True),
        ]

        data = [[player, 80, 20, '', ''],]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.bet(player, bet)
        ui.doubledown(player, bet)
        ui.insures(player, bet)
        ui.insurepay(player, bet)
        ui.loses(player)
        ui.loses_split(player)
        ui.tie(player, bet)
        ui.wins(player, bet)
        ui.ties_split(player, bet)
        ui.wins_split(player, bet)
        act = mock_update_bet.mock_calls[-10:]
        ui.end()

        self.assertEqual(exp, act)

    @patch('blackjack.termui.print')
    @patch('blackjack.cli.TableUI._update_event')
    def test_event_updates(self, mock_update_event, _):
        """The tested methods should call the _update_event() method
        with the player and event text.
        """
        player = players.Player(name='spam', chips=100)
        exp = [
            call(player, 'Shuffles the deck.'),
        ]

        data = [[player, 80, 20, '', ''],]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.shuffles(player)
        act = mock_update_event.mock_calls[-1:]
        ui.end()

        self.assertEqual(exp, act)

    @patch('blackjack.termui.print')
    @patch('blackjack.cli.TableUI._update_hand')
    def test_hand_updates(self, mock_update_hand, _):
        """The tested methods should call the _update_hand() method
        with the player, hand, and event text.
        """
        player = players.Player(name='spam', chips=100)
        hand = cards.Hand([
            cards.Card(11, 0),
            cards.Card(10, 3),
        ])
        handstr = str(hand)
        exp = [
            call(player, hand, 'Takes hand.'),
            call(player, hand, 'Flips card.'),
            call(player, hand, 'Hits.'),
            call(player, hand, 'Stands.'),
        ]

        data = [[player, 80, 20, '', ''],]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.deal(player, hand)
        ui.flip(player, hand)
        ui.hit(player, hand)
        ui.stand(player, hand)
        act = mock_update_hand.mock_calls[-4:]
        ui.end()

        self.assertEqual(exp, act)

    @patch('blackjack.termui.main')
    def test_splits(self, mock_main):
        """When given a player and a bet, splits() should add a row
        to the data table for the split hand, update it with the
        relevant information, and send it to the UI.
        """
        hands = [
            cards.Hand([cards.Card(11, 0),]),
            cards.Hand([cards.Card(11, 3),]),
        ]
        player = players.Player(hands, name='spam', chips=100)
        player2 = players.Player(hands, name='eggs', chips=100)
        new_data = [
            [player, 100, 20, 'J♣', 'Splits hand.'],
            ['  \u2514\u2500', '', 20, 'J♠', ''],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'],
        ]
        exp_call = call().send(('update', new_data))
        unexp_len = len(new_data)

        data = [
            [player, 100, 20, 'J♣ J♠', 'Takes hand.'],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'],
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.splits(player, 20)
        act_call = mock_main.mock_calls[-1]
        act_len = len(data)
        ui.end()

        self.assertEqual(exp_call, act_call)
        self.assertNotEqual(unexp_len, act_len)

    @patch('blackjack.termui.main')
    def test_leaves(self, mock_main):
        """When given a player, leaves() should announce the player is
        leaving and remove the player from the data table. In order to
        avoid the row in the UI just going blank, this call will edit
        self.ctlr.data directly.
        """
        player = players.Player(name='spam', chips=100)
        player2 = players.Player(name='eggs', chips=100)
        new_data = [
            [player, '', '', '', 'Walks away.'],
            [player2, 100, '', '', 'Sits down.'],
        ]
        exp_call = call().send(('update', new_data))
        exp_data = [
            ['', '', '', '', 'Walks away.'],
            [player2, 100, '', '', 'Sits down.'],
        ]

        data = [
            [player, 100, '', '', 'Sits down.'],
            [player2, 100, '', '', 'Sits down.'],
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data

        def update_data(ctlr, data):
            ctlr.data = data

        mock_main.side_effect = update_data(ui.ctlr, [r[:] for r in new_data])
        ui.start()
        ui.leaves(player)
        act_call = mock_main.mock_calls[-1]
        act_data = ui.ctlr.data
        ui.end()

        self.assertEqual(exp_call, act_call)
        self.assertEqual(exp_data, act_data)

    @patch('blackjack.termui.main')
    def test_joins(self, mock_main):
        """When given a player, joins() should add the player to the
        data table in the first empty row.
        """
        player = players.Player(name='spam', chips=100)
        player2 = players.Player(name='eggs', chips=100)
        new_data1 = [
            [player, 100, '', '', 'Sits down.'],
            ['', '', '', '', ''],
        ]
        new_data2 = [
            [player, 100, '', '', 'Sits down.'],
            [player2, 100, '', '', 'Sits down.'],
        ]
        exp_call = [
            call().send(('update', new_data1)),
            call().send(('update', new_data2)),
        ]

        data = [
            ['', '', '', '', ''],
            ['', '', '', '', ''],
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.joins(player)
        ui.ctlr.data = new_data1
        ui.joins(player2)
        act_call = mock_main.mock_calls[-2:]
        ui.end()

        self.assertEqual(exp_call, act_call)
        self.assertNotEqual(new_data2, new_data1)

    @patch('blackjack.termui.main')
    def test__update_bet_split(self, mock_main):
        """When is_split is True, _update_bet should update the split
        row of the data table for the player.
        """
        hands = [
            cards.Hand([cards.Card(11, 0),]),
            cards.Hand([cards.Card(11, 3),]),
        ]
        player = players.Player(hands, name='spam', chips=100)
        player2 = players.Player(name='eggs', chips=100)
        new_data = [
            [player, 100, 20, 'J♣', 'Splits hand.'],
            ['  \u2514\u2500', '', 20, 'J♠', 'Loses.'],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'],
        ]
        exp = call().send(('update', new_data))

        data = [
            [player, 100, 20, 'J♣', 'Splits hand.'],
            ['  \u2514\u2500', '', '', 'J♠', ''],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'],
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui._update_bet(player, 20, 'Loses.', split=True)
        act = mock_main.mock_calls[-1]
        ui.end()

        self.assertEqual(exp, act)

    @patch('blackjack.termui.main')
    def test__update_hand_split(self, mock_main):
        """If sent a split hand, _update_hand() should update the
        split row of the table.
        """
        hands = [
            cards.Hand([cards.Card(11, 0),]),
            cards.Hand([cards.Card(11, 3),]),
        ]
        player = players.Player(hands, name='spam', chips=100)
        player2 = players.Player(name='eggs', chips=100)
        new_data = [
            [player, 100, 20, 'J♣', 'Splits hand.'],
            ['  \u2514\u2500', '', 20, 'J♠ 5♣', 'Hits.'],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'],
        ]
        exp = call().send(('update', new_data))

        data = [
            [player, 100, 20, 'J♣', 'Splits hand.'],
            ['  \u2514\u2500', '', 20, 'J♠', 'Splits hand.'],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'],
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        hands[1].append(cards.Card(5, 0))
        ui._update_hand(player, hands[1], 'Hits.')
        act = mock_main.mock_calls[-1]
        ui.end()

        self.assertEqual(exp, act)

    @patch('blackjack.termui.main')
    def test_cleanup(self, mock_main):
        """When called, cleanup() should clear the bet, hand, and
        event field of every row in the data table, then send it to
        the UI.
        """
        hands = [
            cards.Hand([cards.Card(11, 0),]),
            cards.Hand([cards.Card(11, 3),]),
        ]
        player = players.Player(hands, name='spam', chips=100)
        player2 = players.Player(hands, name='eggs', chips=100)
        new_data = [
            [player, 100, '', '', ''],
            [player2, 100, '', '', ''],
        ]
        exp = call().send(('update', new_data))

        data = [
            [player, 100, 20, 'J♣', 'Splits hand.'],
            ['  \u2514\u2500', '', 20, 'J♠', 'Splits hand.'],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'],
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.cleanup()
        act = mock_main.mock_calls[-1]

        self.assertEqual(exp, act)

    # Input method tests.
    @patch('blackjack.termui.main')
    def test___prompt_calls(self, mock_main):
        """When called, _prompt() should send the UI a prompt for user
        input and return the result.
        """
        exp_call = call().send(('input', 'spam', 'y'))

        ui = cli.TableUI()
        ui.start()
        act_resp = ui._prompt('spam', 'y')
        act_call = mock_main.mock_calls[-1]
        ui.end()

        self.assertEqual(exp_call, act_call)

    @patch('blackjack.termui.main')
    @patch('blackjack.cli.TableUI._prompt')
    def test__yesno_prompt(self, mock_prompt, _):
        """When called, _yesno_prompt() should prompt the user
        for a yes/no answer. The response should be returned.
        """
        exp_resp = model.IsYes('y')
        exp_call = call('Play another round? [yn] > ', 'y')

        ui = cli.TableUI()
        mock_prompt.return_value = 'y'
        ui.start()
        act_resp = ui._yesno_prompt('Play another round?', 'y')
        ui.end()
        act_call = mock_prompt.mock_calls[-1]

        self.assertEqual(exp_resp.value, act_resp.value)
        self.assertEqual(exp_call, act_call)

    @patch('blackjack.termui.main')
    def test__yesno_prompt_unit_valid(self, mock_main):
        """If the user responds with an invalid value, the prompt
        should be repeated.
        """
        exp_resp = model.IsYes('n')

        ui = cli.TableUI()
        mock_main.return_value = (item for item in [None, None, 'z', ' ', 'n'])
        ui.start()
        act_resp = ui._yesno_prompt('spam', 'y')
        ui.end()

        self.assertEqual(exp_resp.value, act_resp.value)

    @patch('blackjack.termui.main')
    @patch('blackjack.cli.TableUI._yesno_prompt')
    def test__yesnos(self, mock_yesno, _):
        """The individual yes/no prompts should sent their prompt and
        a default response value to _yesno_prompt and return the
        response.
        """
        exp_resp = model.IsYes('y')
        exp_calls = [
            call('Double down?', 'y'),
            call('Hit?', 'y'),
            call('Buy insurance?', 'y'),
            call('Play another round?', 'y'),
            call('Split your hand?', 'y'),
        ]

        mock_yesno.return_value = exp_resp
        ui = cli.TableUI()
        ui.start()
        act_resps = []
        act_resps.append(ui.doubledown_prompt())
        act_resps.append(ui.hit_prompt())
        act_resps.append(ui.insure_prompt())
        act_resps.append(ui.nextgame_prompt())
        act_resps.append(ui.split_prompt())
        act_calls = mock_yesno.mock_calls[-5:]
        ui.end()

        for act_resp in act_resps:
            self.assertEqual(exp_resp, act_resp)
        for exp, act in zip(exp_calls, act_calls):
            self.assertEqual(exp, act)
