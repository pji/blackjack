"""
test_cli.py
~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.cli module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from json import load, loads

import pytest

from blackjack import cards, cli, game, model, players, termui, utility


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


# Tests for command line parsing.
# Fixtures for parse_cli.
@pytest.fixture
def engine(mocker, request):
    """A basic test of the command line."""
    marker = request.node.get_closest_marker('argv')
    mocker.patch('sys.argv', list(marker.args))
    mocker.patch('blackjack.cards.randrange', return_value=65)
    args = cli.parse_cli()
    yield cli.build_game(args)


# Tests for parse_cli.
@pytest.mark.argv(['blackjack',])
def test_cli_default_game(engine):
    """When given no options, `blackjack` should start a default
    game with four computer players and a human player.
    """
    assert engine.ui.seats == 6
    assert len(engine.deck) == 52 * 6
    assert engine.dealer == players.Dealer(name='Dealer')
    assert len(engine.playerlist) == 5
    assert engine.playerlist[-1] == players.UserPlayer(name='You', chips=200)
    assert engine.buyin == 20
    assert engine.save_file == 'save.json'
    assert engine.deck_size == 6
    assert not engine.deck_cut
    assert not engine.running_count


@pytest.mark.argv('blackjack', '-a')
def test_cli_automated_game(engine):
    """Given the -a option, the game should not include
    a :class:`UserPlayer`.
    """
    for player in engine.playerlist:
        assert not isinstance(player, players.UserPlayer)


@pytest.mark.argv('blackjack', '-b 100')
def test_cli_change_buyin(engine):
    """When passed the -b option, change amount of chips needed to
    buy into each hand.
    """
    assert engine.buyin == 100


@pytest.mark.argv('blackjack', '-c 100')
def test_cli_change_player_chips(engine):
    """When passed the -c option, change amount of chips given to
    the user player.
    """
    assert engine.playerlist[-1].chips == 100


@pytest.mark.argv('blackjack', '-C')
def test_cli_cut_deck(engine):
    """When passed the -C option, cut a random number of cards
    between 60 and 75 from the bottom of the deck to make card
    counting harder.
    """
    assert len(engine.deck) == 52 * 6 - 65


@pytest.mark.argv('blackjack', '-d 4')
def test_cli_change_deck_size(engine):
    """When passed the -d option, change the number of standard
    decks used to build the deck for the game.
    """
    assert engine.deck_size == 4
    assert len(engine.deck) == 52 * 4


@pytest.mark.argv('blackjack', '-p 7')
def test_cli_change_number_of_computer_players(engine):
    """When passed the -p option, change the number of computer
    players in the game.
    """
    assert engine.ui.seats == 7 + 2
    assert len(engine.playerlist) == 7 + 1


@pytest.mark.argv('blackjack', '-s spam')
def test_cli_change_save_file(engine):
    """When passed the -s option and the path to a save file, change
    the save file location to that path.
    """
    assert engine.save_file == 'spam'


@pytest.mark.argv('blackjack', '-K')
def test_cli_count_cards(engine):
    """When passed the -K option, display the running count in the UI."""
    assert engine.running_count


@pytest.mark.argv('blackjack', '-f tests/data/savefile')
def test_cli_restore_game(engine):
    """When passed a -f option followed by a file path, create a
    new game from the save information stored in the file.
    """
    path = 'tests/data/savefile'
    with open(path) as fh:
        expected = load(fh)
    actual = loads(engine.serialize())
    assert actual == expected


@pytest.mark.argv('blackjack', '-f tests/data/savefile', '-K')
def test_cli_restore_game_and_count_cards(engine):
    """When passed a -f option followed by a file path and -K,
    create a new game from the save information stored in the file.
    """
    path = 'tests/data/savefile'
    with open(path) as fh:
        expected = load(fh)
    actual = loads(engine.serialize())
    assert actual == expected
    assert engine.ui.show_status


@pytest.mark.argv('blackjack', '-L')
def test_cli_use_LogUI(engine):
    """When passed the -L option, change the UI to use LogUI
    instead of TableUI.
    """
    assert isinstance(engine.ui, cli.LogUI)
