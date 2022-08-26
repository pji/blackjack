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

from blackjack import cards, cli, game, model, players, termui, utility


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
        title_ = [f'{line}\n' for line in utility.splash_title]
        lines = [
            '\n',
            *title_,
            '\n',
            self.tmp.format('Player', 'Action', 'Hand'),
            '\u2500' * 50 + '\n',
        ]
        exp = ''.join(lines)

        with capture() as (out, err):
            ui = cli.LogUI(True)
            ui.start(splash_title=utility.splash_title)
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
        title_ = [f'{line}\n' for line in utility.splash_title]
        lines = [
            '\u2500' * 50 + '\n',
            '\n',
            '\n',
            *title_,
            '\n',
            self.tmp.format('Player', 'Action', 'Hand'),
            '\u2500' * 50 + '\n',
        ]
        exp = ''.join(lines)

        with capture() as (out, err):
            ui = cli.LogUI(True)
            ui.cleanup(splash_title=utility.splash_title)
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

    # Test _multichar_prompt().
    @patch('blackjack.cli.input', return_value='20')
    def test__multichar_prompt(self, mock_input):
        """Given a prompt and a default value, prompt the user for
        multiple characters of input.
        """
        # Expected value.
        prompt = 'spam'
        exp_resp = mock_input()
        exp_call = call(prompt)

        # Test data and state
        ui = cli.LogUI()

        # Run test and gather actuals.
        act_resp = ui._multichar_prompt(prompt)
        act_call = mock_input.mock_calls[-1]

        # Determine test result.
        self.assertEqual(exp_resp, act_resp)
        self.assertEqual(exp_call, act_call)

    @patch('blackjack.cli.LogUI._multichar_prompt', return_value='20')
    def test_bet_prompt(self, mock_input):
        """When called, prompt the user for the bet amount and return
        that amount as a Bet.
        """
        # Set up for expected values.
        bet_min = 20
        bet_max = 500

        # Expected value.
        exp_bet = model.Bet(int(mock_input()))
        exp_call = call(
            f'How much do you wish to bet? [{bet_min}-{bet_max}]',
            str(bet_min)
        )

        # Test data and state.
        ui = cli.LogUI()

        # Run test and gather actuals.
        act_bet = ui.bet_prompt(bet_min, bet_max)
        act_call = mock_input.mock_calls[-1]

        # Determine test results.
        self.assertEqual(exp_bet, act_bet)
        self.assertEqual(exp_call, act_call)

    @patch('blackjack.cli.print')
    @patch('blackjack.cli.input')
    def test_bet_prompt_invalid_input(self, mock_input, mock_print):
        """When called, prompt the user for the bet amount and return
        that amount as a Bet.
        """
        # Set up for expected values.
        bet_min = 20
        bet_max = bet_min + 100

        # Expected value.
        exp_bet = model.Bet(bet_min)
        exp_input_calls = [
            call(f'How much do you wish to bet? [{bet_min}-{bet_max}]'),
            call(f'How much do you wish to bet? [{bet_min}-{bet_max}]'),
            call(f'How much do you wish to bet? [{bet_min}-{bet_max}]'),
        ]
        exp_error_calls = [
            call('Invalid input.'),
            call('Invalid input.'),
        ]

        # Test data and state.
        mock_input.side_effect = ['y', f'{bet_max + 1}', f'{exp_bet.value}']
        ui = cli.LogUI()

        # Run test and gather actuals.
        act_bet = ui.bet_prompt(bet_min, bet_max)
        act_input_calls = mock_input.mock_calls
        act_error_calls = mock_print.mock_calls

        # Determine test results.
        self.assertEqual(exp_input_calls, act_input_calls)
        self.assertEqual(exp_error_calls, act_error_calls)
        self.assertEqual(exp_bet, act_bet)

    @patch('blackjack.cli.LogUI._multichar_prompt', return_value='20')
    def test_insure_prompt(self, mock_input):
        """When called, prompt the user for the insure amount and
        return that amount as a Bet.
        """
        # Set up for expected values.
        insure_max = 500

        # Expected value.
        exp_insure = model.Bet(int(mock_input()))
        exp_call = call(
            f'How much insurance do you want? [0–{insure_max}]',
            str(0)
        )

        # Test data and state.
        ui = cli.LogUI()

        # Run test and gather actuals.
        act_insure = ui.insure_prompt(insure_max)
        act_call = mock_input.mock_calls[-1]

        # Determine test results.
        self.assertEqual(exp_insure, act_insure)
        self.assertEqual(exp_call, act_call)

    @patch('blackjack.cli.print')
    @patch('blackjack.cli.input')
    def test_insure_prompt_invalid_input(self, mock_input, mock_print):
        """When called, prompt the user for the insure amount and
        return that amount as a Bet.
        """
        # Set up for expected values.
        insure_max = 500

        # Expected value.
        exp_insure = model.Bet(insure_max - 50)
        exp_input_calls = [
            call(f'How much insurance do you want? [0–{insure_max}]'),
            call(f'How much insurance do you want? [0–{insure_max}]'),
            call(f'How much insurance do you want? [0–{insure_max}]'),
        ]
        exp_error_calls = [
            call('Invalid input.'),
            call('Invalid input.'),
        ]

        # Test data and state.
        mock_input.side_effect = [
            'y',
            f'{insure_max + 1}',
            f'{exp_insure.value}'
        ]
        ui = cli.LogUI()

        # Run test and gather actuals.
        act_insure = ui.insure_prompt(insure_max)
        act_input_calls = mock_input.mock_calls
        act_error_calls = mock_print.mock_calls

        # Determine test results.
        self.assertEqual(exp_input_calls, act_input_calls)
        self.assertEqual(exp_error_calls, act_error_calls)
        self.assertEqual(exp_insure, act_insure)

    # Test _yesno_prompt().
    @patch('blackjack.cli.input')
    def test_yesno_prompt(self, mock_input):
        """Given a prompt and a default value, prompt the user for a
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

    @patch('blackjack.cli.print')
    @patch('blackjack.cli.input')
    def test_yesno_prompt_invalid_input(self, mock_input, mock_print):
        """Given a prompt and a default value, prompt the user for a
        yes/no answer until they give a valid answer. Then return the
        valid response.
        """
        exp_resp = model.IsYes('y')
        exp_input_calls = [
            call('spam [yn] > '),
            call('spam [yn] > '),
            call('spam [yn] > '),
        ]
        exp_error_calls = [
            call('Invalid input.'),
            call('Invalid input.'),
        ]

        mock_input.side_effect = ('6', 'k', 'y')
        ui = cli.LogUI()
        act_resp = ui._yesno_prompt('spam', 'y')
        act_input_calls = mock_input.mock_calls
        act_error_calls = mock_print.mock_calls

        self.assertEqual(exp_resp.value, act_resp.value)
        self.assertEqual(exp_input_calls, act_input_calls)
        self.assertEqual(exp_error_calls, act_error_calls)

    @patch('blackjack.cli.LogUI._yesno_prompt')
    def test_prompt_yesnos(self, mock_input):
        """The input methods that ask yes/no questions should call
        _yesno_prompt() with a prompt and a default, and they should
        return the response from _yesno_prompt().
        """
        prompts = [
            'Double down?',
            'Hit?',
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

    def test_automated_players_only(self):
        """Given the -a option, the game should not include
        a UserPlayer.
        """
        # The not expected value:
        not_exp = players.UserPlayer

        # Test data and state.
        sys.argv = ['python -m blackjack', f'-a']

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        act_list = engine.playerlist

        # Determine test result.
        for act in act_list:
            self.assertNotIsInstance(act, not_exp)

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

    def test_restore_from_file_with_counting(self):
        """When passed a -f option followed by a file path and -K,
        create a new game from the save information stored in the file.
        """
        # Set up for expected value.
        path = 'tests/data/savefile'
        with open(path) as fp:

            # Expected values.
            exp = load(fp)
        exp_show_status = True

        # Test data and state.
        sys.argv = [
            'python -m blackjack',
            '-f tests/data/savefile',
            '-K',
        ]

        # Run test.
        args = cli.parse_cli()
        engine = cli.build_game(args)

        # Gather actual data.
        serial = engine.serialize()
        act = loads(serial)
        act_show_status = engine.ui.show_status

        # Determine test result.
        for key in exp:
            e = key, exp[key]
            a = key, act[key]
            self.assertEqual(e, a)
        self.assertDictEqual(exp, act)
        self.assertEqual(exp_show_status, act_show_status)

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
