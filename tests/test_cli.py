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

import pytest
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
# Tests for LogUI
# LogUI common values.
tmp = '{:<15} {:<15} {:<}'


# Fixtures for LogUI.
@pytest.fixture
def logui():
    """A :class:`LogUI` object for testing."""
    yield cli.LogUI()


# Tests for LogUI initialization.
def test_LogUI_init_default():
    """Given no parameters, :class:`LogUI` should use default values
    for the object's parameters.
    """
    optionals = {
        'is_interactive': False,
    }
    ui = cli.LogUI()
    for attr in optionals:
        assert getattr(ui, attr) == optionals[attr]


def test_LogUI_init_optionals():
    """Given parameters, :class:`LogUI` should use the given values
    for the object's parameters.
    """
    optionals = {
        'is_interactive': True,
    }
    ui = cli.LogUI(**optionals)
    for attr in optionals:
        assert getattr(ui, attr) == optionals[attr]


# Tests for LogUI loop management.
def test_LogUI_end(capsys, logui):
    """When called, :meth:`LogUI.end` should print the footers for
    the game output.
    """
    logui.end(True)
    captured = capsys.readouterr()
    assert captured.out == '\n'.join([
        '\u2500' * 50,
        ''
    ]) + '\n'


def test_LogUI_start(capsys, logui):
    """When called, :meth:`LogUI.start` should print the headers for
    the game output.
    """
    logui.start(splash_title=utility.splash_title)
    captured = capsys.readouterr()
    assert captured.out == '\n'.join([
        '',
        *utility.splash_title,
        '',
        tmp.format('Player', 'Action', 'Hand'),
        '\u2500' * 50
    ]) + '\n'


# Tests for LogUI private update methods.
def test_LogUI__update_bet(capsys, logui):
    """Given a player, bet, and event, :meth:`LogUI._update_bet`
    should update the UI with the event.
    """
    player = players.Player(name='spam', chips=200)
    bet = 20
    event = 'Bet.'
    logui._update_bet(player, bet, event)
    captured = capsys.readouterr()
    assert captured.out == tmp.format(player, event, f'{bet} (200)\n')


def test_LogUI__update_event(capsys, logui):
    """Given a player, bet, and event, :meth:`LogUI._update_event`
    should update the UI with the event.
    """
    player = players.Player(name='spam', chips=200)
    event = 'eggs'
    logui._update_event(player, event)
    captured = capsys.readouterr()
    assert captured.out == tmp.format(player, event, '') + '\n'


def test_LogUI__update_hand(capsys, logui):
    """Given a player, bet, and event, :meth:`LogUI._update_hand`
    should update the UI with the event.
    """
    player = players.Player(name='spam', chips=200)
    hand = cards.Hand([cards.Card(1, 0), cards.Card(2, 0)])
    event = 'eggs'
    logui._update_hand(player, event, hand)
    captured = capsys.readouterr()
    assert captured.out == tmp.format(player, hand, event) + '\n'


def test_LogUI__update_status(capsys, logui):
    """Given an event, :meth:`LogUI._update_status` should report that
    event to the user.
    """
    label = 'Card count:'
    event = '5'
    logui._update_status(label, event)
    captured = capsys.readouterr()
    assert captured.out == tmp.format(label, '', event) + '\n'


# Tests for LogUI public update methods.
def test_LogUI_all_bet_updates(mocker, logui):
    """The methods tested should send :meth:`LogUI._update_bet` a
    player, a bet, and event text for display to the user.
    """
    mock_bet = mocker.patch('blackjack.cli.LogUI._update_bet')
    player = players.Player(name='spam')
    bet = 20
    expected = [
        mocker.call(player, bet, 'Bet.'),
        mocker.call(player, bet, 'Double down.'),
        mocker.call(player, bet, 'Insures.'),
        mocker.call(player, bet, 'Insure pay.'),
        mocker.call(player, bet, 'Tie.'),
        mocker.call(player, bet, 'Tie.'),
        mocker.call(player, bet, 'Wins.'),
        mocker.call(player, bet, 'Wins.'),
        mocker.call(player, bet, 'Splits.'),
        mocker.call(player, '', 'Loses.'),
        mocker.call(player, '', 'Loses.'),
    ]

    logui.bet(player, bet)
    logui.doubledown(player, bet)
    logui.insures(player, bet)
    logui.insurepay(player, bet)
    logui.tie(player, bet)
    logui.ties_split(player, bet)
    logui.wins(player, bet)
    logui.wins_split(player, bet)
    logui.splits(player, bet)
    logui.loses(player)
    logui.loses_split(player)
    assert mock_bet.mock_calls == expected


def test_LogUI_all_event_updates(mocker, logui):
    """The methods tested should send :meth:`LogUI._update_event` a
    player and event text for display to the user.
    """
    mock_event = mocker.patch('blackjack.cli.LogUI._update_event')
    player = players.Player(name='spam')
    expected = [
        mocker.call(player, 'Joins.'),
        mocker.call(player, 'Leaves.'),
        mocker.call(player, 'Shuffles.'),
    ]

    logui.joins(player)
    logui.leaves(player)
    logui.shuffles(player)
    assert mock_event.mock_calls == expected


def test_LogUI_all_hand_updates(mocker, logui):
    """The methods tested should send :meth:`LogUI._update_hand` a
    player and event text for display to the user.
    """
    mock_event = mocker.patch('blackjack.cli.LogUI._update_hand')
    player = players.Player(name='spam')
    hand = cards.Hand([cards.Card(1, 0), cards.Card(2, 0)])
    expected = [
        mocker.call(player, hand, 'Dealt hand.'),
        mocker.call(player, hand, 'Flip.'),
        mocker.call(player, hand, 'Hit.'),
        mocker.call(player, hand, 'Stand.'),
    ]

    logui.deal(player, hand)
    logui.flip(player, hand)
    logui.hit(player, hand)
    logui.stand(player, hand)
    assert mock_event.mock_calls == expected


def test_LogUI_cleanup(capsys, logui):
    """When called, :meth:`LogUI.cleanup` should print the footer and
    the header to the UI.
    """
    logui.cleanup(splash_title=utility.splash_title)
    captured = capsys.readouterr()
    assert captured.out == '\n'.join([
        '\u2500' * 50,
        '',
        '',
        *utility.splash_title,
        '',
        tmp.format('Player', 'Action', 'Hand'),
        '\u2500' * 50
    ]) + '\n'


def test_LogUI_update_count(mocker, logui):
    """When an :meth:`LogUI.update_count` event is received, a message
    should be displayed that shows the new card count.
    """
    mock_status = mocker.patch('blackjack.cli.LogUI._update_status')
    logui.update_count(10)
    assert mock_status.mock_calls == [
        mocker.call('Running count:', 10),
    ]


# Tests for LogUI private input methods.
def test_LogUI__multichar_prompt(mocker, logui):
    """Given a prompt and a default value,
    :meth:`LogUI._multichar_prompt` should
    prompt the user for multiple characters
    of input.
    """
    mock_input = mocker.patch('blackjack.cli.input', return_value='20')
    assert logui._multichar_prompt('spam') == '20'
    assert mock_input.mock_calls == [
        mocker.call('spam')
    ]


def test_LogUI__yesno_prompt(mocker, logui):
    """Given a prompt and a default value, :meth:`LogUI._yesno_prompt`
    should prompt the user for a yes/no answer and return the result.
    """
    mock_input = mocker.patch('blackjack.cli.input', return_value='n')
    assert logui._yesno_prompt('spam', 'y') == model.IsYes('n')
    assert mock_input.mock_calls == [
        mocker.call('spam [yn] > ')
    ]


def test_LogUI__yesno_prompt_invalid(mocker, logui):
    """Given a prompt and a default value, :meth:`LogUI._yesno_prompt`
    should prompt the user for a yes/no answer and return the result.
    If the user provides invalid input, the method should prompt again
    until valid input is received.
    """
    mock_error = mocker.patch('blackjack.cli.print')
    mock_input = mocker.patch(
        'blackjack.cli.input',
        side_effect=['6', 'k', 'y']
    )
    assert logui._yesno_prompt('spam', 'y') == model.IsYes('y')
    assert mock_input.mock_calls == [
        mocker.call('spam [yn] > '),
        mocker.call('spam [yn] > '),
        mocker.call('spam [yn] > '),
    ]
    assert mock_error.mock_calls == [
        mocker.call('Invalid input.'),
        mocker.call('Invalid input.'),
    ]


# Tests for LogUI public input methods.
def test_LogUI_all_yesno_prompts(mocker, logui):
    """The input methods that ask yes/no questions should call
    :meth:`LogUI._yesno_prompt` with a prompt and a default, and
    they should return the response.
    """
    mock_yn = mocker.patch(
        'blackjack.cli.LogUI._yesno_prompt',
        return_value=model.IsYes('n')
    )
    assert logui.doubledown_prompt() == model.IsYes('n')
    assert logui.hit_prompt() == model.IsYes('n')
    assert logui.nextgame_prompt() == model.IsYes('n')
    assert logui.split_prompt() == model.IsYes('n')
    assert mock_yn.mock_calls == [
        mocker.call('Double down?', 'y'),
        mocker.call('Hit?', 'y'),
        mocker.call('Next game?', 'y'),
        mocker.call('Split?', 'y'),
    ]


def test_LogUI_bet_prompt(mocker, logui):
    """When called, :meth:`LogUI.bet_prompt` should prompt the user
    for the bet amount and return that amount as a :class:`model.Bet`.
    """
    mock_prompt = mocker.patch(
        'blackjack.cli.LogUI._multichar_prompt',
        return_value='20'
    )
    assert logui.bet_prompt(20, 500) == model.Bet('20')
    assert mock_prompt.mock_calls == [
        mocker.call('How much do you wish to bet? [20-500]', '20'),
    ]


def test_LogUI_bet_prompt_invalid(mocker, logui):
    """When called, :meth:`LogUI.bet_prompt` should prompt the user
    for the bet amount and return that amount as a :class:`model.Bet`.
    If the user provides invalid input, the method should prompt again
    until valid input is received.
    """
    mock_error = mocker.patch('blackjack.cli.print')
    mock_prompt = mocker.patch(
        'blackjack.cli.LogUI._multichar_prompt',
        side_effect=['y', '501', '100']
    )
    assert logui.bet_prompt(20, 500) == model.Bet('100')
    assert mock_prompt.mock_calls == [
        mocker.call('How much do you wish to bet? [20-500]', '20'),
        mocker.call('How much do you wish to bet? [20-500]', '20'),
        mocker.call('How much do you wish to bet? [20-500]', '20'),
    ]
    assert mock_error.mock_calls == [
        mocker.call('Invalid input.'),
        mocker.call('Invalid input.'),
    ]


def test_LogUI_insure_prompt(mocker, logui):
    """When called, :meth:`LogUI.insure_prompt` should prompt
    the user for the insurance amount and return that amount as
    a :class:`model.Bet`.
    """
    mock_prompt = mocker.patch(
        'blackjack.cli.LogUI._multichar_prompt',
        return_value='20'
    )
    assert logui.insure_prompt(500) == model.Bet('20')
    assert mock_prompt.mock_calls == [
        mocker.call('How much insurance do you want? [0–500]', '0'),
    ]


def test_LogUI_insure_prompt_invalid(mocker, logui):
    """When called, :meth:`LogUI.insure_prompt` should prompt
    the user for the insurance amount and return that amount as
    a :class:`model.Bet`. If the user provides invalid input,
    the method should prompt again until valid input is received.
    """
    mock_error = mocker.patch('blackjack.cli.print')
    mock_prompt = mocker.patch(
        'blackjack.cli.LogUI._multichar_prompt',
        side_effect=['y', '501', '100']
    )
    assert logui.insure_prompt(500) == model.Bet('100')
    assert mock_prompt.mock_calls == [
        mocker.call('How much insurance do you want? [0–500]', '0'),
        mocker.call('How much insurance do you want? [0–500]', '0'),
        mocker.call('How much insurance do you want? [0–500]', '0'),
    ]
    assert mock_error.mock_calls == [
        mocker.call('Invalid input.'),
        mocker.call('Invalid input.'),
    ]


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
