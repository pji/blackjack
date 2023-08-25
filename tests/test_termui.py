"""
test_termui.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.termui module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import unittest as ut
from unittest.mock import call, patch, PropertyMock

import pytest
from blessed import Terminal
from blessed.keyboard import Keystroke

from blackjack import cards, game, model, players, termui


# Common data.
bold = '\x1b[1m'
loc = '\x1b[{};{}H'
topleft = '\x1b[1;2H'


# Tests for Box.
def test_box_attrs():
    """When an attribute is requested, :class:`Box` should return
    the box character for that attribute.
    """
    attrs = {
        'top': '\u2500',
        'bot': '\u2500',
        'side': '\u2502',
        'ltop': '\u250c',
        'rtop': '\u2510',
        'mtop': '\u252c',
        'lbot': '\u2514',
        'rbot': '\u2518',
        'mbot': '\u2534',
        'lside': '\u251c',
        'rside': '\u2524',
        'mid': '\u253c',
    }
    box = termui.Box()
    for attr in attrs:
        assert getattr(box, attr) == attrs[attr]


def test_box_kind_change_kind():
    """If given a kind, :attr:`Box.kind` should change the kind
    of box characters returned.
    """
    expected = ['\u2500', '\u2501', '\u2508']

    box = termui.Box('light')
    actual = [box.top,]
    box.kind = 'heavy'
    actual.append(box.top)
    box.kind = 'light_quadruple_dash'
    actual.append(box.top)

    assert expected == actual


def test_box_kind_custom():
    """If given a kind of 'custom' string of characters, the box
     object should return the custom characters and it's kind
     should be 'custom'.
    """
    exp_kind = 'custom'
    exp_chars = 'abcdefghijklmn'
    exp_sample = 'g'

    box = termui.Box(custom=exp_chars)
    act_kind = box.kind
    act_chars = box._chars
    act_sample = box.mtop

    assert exp_kind == act_kind
    assert exp_chars == act_chars
    assert exp_sample == act_sample


def test_kind_invalid_custom_string():
    """The passed custom string is not exactly fourteen characters
    long, a ValueError should be raised.
    """
    with pytest.raises(ValueError):
        box = termui.Box(custom='bad')


# Tests for Splash.
def test_splash(capsys, mocker):
    """When called with a sequence of strings, :func:`termui.splash`
    should draw those strings in the middle of the terminal and wait
    until any key is pressed.
    """
    prompt = 'Press any key to continue.'
    term = Terminal()
    text = ['spam', 'eggs',]
    mocker.patch('blessed.Terminal.inkey', side_effect=['\n',])
    termui.splash(text)
    captured = capsys.readouterr()
    assert captured.out == '\n'.join([
        loc.format(
            term.height // 2 - len(text) // 2 + 1,
            term.width // 2 - len(text[0]) // 2 + 1
        ) + text[0],
        loc.format(
            term.height // 2 - len(text) // 2 + 2,
            term.width // 2 - len(text[1]) // 2 + 1
        ) + text[1],
        loc.format(
            term.height,
            term.width // 2 - len(prompt) // 2 + 1
        ) + prompt,
    ]) + '\n'


# Tests for Table.
data = [[1, 2], [3, 4]]
cls = '\x1b[2J'
fields = [
    ('Name', '{:>10}'),
    ('Value', '{:>10}'),
]
fmt = '{:<80}'
frame = '\u2500' * 23
head = ' ' + ' '.join('{:<10}'.format(f[0]) for f in fields)
home = '\x1b[H'
loc = '\x1b[{};{}H'
title = 'Eggs'
row = ' ' + ' '.join(field[1] for field in fields) + ' '


# Table fixtures.
@pytest.fixture
def table_main():
    """A simple Table to test."""
    ctlr = termui.Table(title, fields, data=data)
    main = termui.main(ctlr)
    yield main


@pytest.fixture
def table_main_with_status():
    """A simple Table to test."""
    ctlr = termui.Table(title, fields, data=data, show_status=True)
    main = termui.main(ctlr)
    yield main


@pytest.fixture
def table_draw_test(request, capsys, table_main):
    """A basic test of :meth:`blackjack.termui.Table._draw_cell`."""
    marker = request.node.get_closest_marker('msg')

    next(table_main)
    table_main.send(marker.args[0])
    del table_main

    captured = capsys.readouterr()
    return captured.out


@pytest.fixture
def table_draw_with_status_test(request, capsys, table_main_with_status):
    """A basic test of :meth:`blackjack.termui.Table._draw_cell`."""
    next(table_main_with_status)
    marker = request.node.get_closest_marker('msg')
    table_main_with_status.send(marker.args[0])
    del table_main_with_status

    captured = capsys.readouterr()
    return captured.out


@pytest.fixture
def table_input_test(request, capsys, table_main, mocker):
    """A basic test of :meth:`blackjack.termui.Table.input`."""
    marker = request.node.get_closest_marker('msg')

    input_ = marker.args[1]
    mocker.patch('clireader.view_text', return_value=None)
    mocker.patch('blessed.Terminal.inkey', side_effect=input_)

    next(table_main)
    returned = table_main.send(marker.args[0])
    del table_main

    captured = capsys.readouterr()
    return captured.out, returned


@pytest.fixture
def table_input_with_status_test(
    request, capsys, table_main_with_status, mocker
):
    """A basic test of :meth:`blackjack.termui.Table.input`."""
    marker = request.node.get_closest_marker('msg')

    input_ = ['n',]
    if len(marker.args) > 1:
        input_ = marker.args[1]
    mocker.patch('blessed.Terminal.inkey', side_effect=input_)

    next(table_main_with_status)
    returned = table_main_with_status.send(marker.args[0])
    del table_main_with_status

    captured = capsys.readouterr()
    return captured.out, returned


# Tests for Table initialization.
def test_Table_init_attributes():
    """When initialized, :class:`Table` should accept values for the
    class's required attributes.
    """
    expected = {
        'title': 'Spam',
        'fields': (
            termui.Field('Eggs', '{}'),
            termui.Field('Baked Beans', '{}'),
        ),
    }
    table = termui.Table(**expected)
    for attr in expected:
        assert getattr(table, attr) == expected[attr]
    assert table.data == [['', ''],]


def test_Table_init_attributes_optional():
    """When initialized, :class:`Table` should accept values for the
    class's optional attributes.
    """
    expected = {
        'title': 'Spam',
        'fields': (
            termui.Field('Eggs', '{}'),
            termui.Field('Baked Beans', '{}'),
        ),
        'frame': termui.Box('light'),
        'data': [[0, 1, 2], [3, 4, 5],],
        'term': Terminal(),
        'row_sep': True,
        'rows': 2,
        'show_status': True,
    }
    table = termui.Table(**expected)
    for attr in expected:
        try:
            actual_value = getattr(table, attr)
            expected_value = expected[attr]
            assert actual_value == expected_value
        except AssertionError:
            raise AssertionError(f'{attr} {actual_value} == {expected_value}')


def test_Table_init_data_changes_rows():
    """When initialized, :class:`Table` should accept values for the
    class's required attributes. Setting the value for :attr:`Table.data`
    should cause :attr:`Table.rows` to be the length of the value of
    :attr:`Table.data`
    """
    expected = {
        'title': 'Spam',
        'fields': (
            termui.Field('Eggs', '{}'),
            termui.Field('Baked Beans', '{}'),
        ),
        'data': [['', ''], ['', ''],],
    }
    table = termui.Table(**expected)
    for attr in expected:
        assert getattr(table, attr) == expected[attr]
    assert table.rows == 2


def test_Table_init_rows_changes_data():
    """When initialized, :class:`Table` should accept values for the
    class's required attributes. Setting the value for :attr:`Table.rows`
    should cause :attr:`Table.data` to have that length.
    """
    expected = {
        'title': 'Spam',
        'fields': (
            termui.Field('Eggs', '{}'),
            termui.Field('Baked Beans', '{}'),
        ),
        'rows': 2,
    }
    table = termui.Table(**expected)
    for attr in expected:
        assert getattr(table, attr) == expected[attr]
    assert table.data == [['', ''], ['', ''],]


# Tests for table._draw_cell.
@pytest.mark.msg(('_draw_cell', 0, 1, 'spam'))
def test_Table__draw_cell(table_draw_test):
    """When given the coordinates of a cell to draw,
    :meth:`blackjack.termui.Table._draw_cell` should
    draw that cell in the UI.
    """
    assert table_draw_test == (
        loc.format(5, 13)
        + fields[1][1].format('spam')
        + '\n'
    )


@pytest.mark.msg(('_draw_cell', 0, 1, '01234567890123456789'))
def test_Table__draw_cell_truncate(table_draw_test):
    """When given the coordinates of a cell to draw,
    :meth:`blackjack.termui.Table._draw_cell` should
    draw that cell in the UI. If the text overflows the
    width of the cell, the text should be truncated to
    the width of the cell.
    """
    assert table_draw_test == (
        loc.format(5, 13)
        + fields[1][1].format('01234567890123456789'[:10])
        + '\n'
    )


@pytest.mark.msg(('_draw_cell', 0, 1, 1234567890123456789))
def test_Table__draw_cell_truncate_with_int(table_draw_test):
    """When given the coordinates of a cell to draw,
    :meth:`blackjack.termui.Table._draw_cell` should
    draw that cell in the UI. If the text overflows the
    width of the cell, the text should be truncated to
    the width of the cell.
    """
    assert table_draw_test == (
        loc.format(5, 13)
        + fields[1][1].format('1234567890123456789'[:10])
        + '\n'
    )


# Tests for Table.clear.
@pytest.mark.msg(('clear',))
def test_Table_clear(table_draw_test):
    """When called, :meth:`blackjack.termui.Table.clear` should
    erase everything on the UI.
    """
    assert table_draw_test == ''.join(
        loc.format(y, 1) + ' ' * 80 + '\n'
        for y in range(1, 9)
    )


# Tests for Table.draw.
@pytest.mark.msg(('draw',))
def test_Table_draw(table_draw_test):
    """When called, :meth:`blackjack.termui.Table.draw` should
    draw the entire UI to the terminal.
    """
    assert table_draw_test == '\n'.join([
        topleft + bold + title,
        loc.format(2, 2) + '',
        loc.format(3, 2) + head,
        loc.format(4, 2) + frame,
        loc.format(5, 1) + row.format(*data[0]),
        loc.format(6, 1) + row.format(*data[1]),
        loc.format(7, 1) + frame,
    ]) + '\n'


@pytest.mark.msg(('draw',))
def test_Table_draw(table_draw_test):
    """When called, :meth:`blackjack.termui.Table.draw` should
    draw the entire UI to the terminal.
    """
    assert table_draw_test == '\n'.join([
        topleft + bold + title,
        loc.format(2, 2) + '',
        loc.format(3, 2) + head,
        loc.format(4, 2) + frame,
        loc.format(5, 1) + row.format(*data[0]),
        loc.format(6, 1) + row.format(*data[1]),
        loc.format(7, 1) + frame,
    ]) + '\n'


@pytest.mark.msg(('draw',))
def test_Table_draw(table_draw_with_status_test):
    """When called, :meth:`blackjack.termui.Table.draw` should
    draw the entire UI to the terminal.
    """
    assert table_draw_with_status_test == '\n'.join([
        topleft + bold + title,
        loc.format(2, 2) + '',
        loc.format(3, 2) + head,
        loc.format(4, 2) + frame,
        loc.format(5, 1) + row.format(*data[0]),
        loc.format(6, 1) + row.format(*data[1]),
        loc.format(7, 1) + frame,
        loc.format(8, 1) + ' ' * 80,
        loc.format(8, 2) + 'Count: 0',
        loc.format(9, 1) + frame,
    ]) + '\n'


# Tests for Table.error.
@pytest.mark.msg(('error', 'spam',))
def test_Table_error(table_draw_test):
    """When called with a message, :meth:`blackjack.termui.Table.error`
    should write the error to the UI.
    """
    msg = 'spam'
    assert table_draw_test == loc.format(9, 2) + fmt.format(msg) + '\n'


# Tests for Table.input.
@pytest.mark.msg(('input', 'spam',), ['n',])
def test_Table_input(table_input_test):
    """When called with a prompt, :meth:`blackjack.termui.Table.input`
    should write the prompt to the UI and return the response from
    the user.
    """
    displayed, returned = table_input_test
    assert displayed == '\n'.join([
        loc.format(8, 2) + fmt.format('spam'),
        loc.format(8, 2) + fmt.format(''),
    ]) + '\n'
    assert returned == 'n'


@pytest.mark.msg(('input', 'spam', 'n'), ['',])
def test_Table_input_default(table_input_test):
    """When called with a prompt, :meth:`blackjack.termui.Table.input`
    should write the prompt to the UI and return the response from
    the user.
    """
    displayed, returned = table_input_test
    assert displayed == '\n'.join([
        loc.format(8, 2) + fmt.format('spam'),
        loc.format(8, 2) + fmt.format(''),
    ]) + '\n'
    assert returned == 'n'


@pytest.mark.msg(('input', 'spam',), ['n',])
def test_Table_input_with_status(table_input_with_status_test):
    """When called with a prompt, :meth:`blackjack.termui.Table.input`
    should write the prompt to the UI and return the response from
    the user.
    """
    displayed, returned = table_input_with_status_test
    assert displayed == '\n'.join([
        loc.format(10, 2) + fmt.format('spam'),
        loc.format(10, 2) + fmt.format(''),
    ]) + '\n'
    assert returned == 'n'


@pytest.mark.msg(('input', 'spam',), [
    Keystroke('\x1b'),
    'x',
    'n',
])
def test_Table_input_esc_to_help(table_input_test):
    """When called with a prompt, :meth:`blackjack.termui.Table.input`
    should write the prompt to the UI and return the response from
    the user. The ESC key should send the user to the help screen.
    """
    displayed, returned = table_input_test
    assert displayed == '\n'.join([
        loc.format(8, 2) + fmt.format('spam'),
        loc.format(8, 2) + fmt.format(''),
        home + cls,
        topleft + bold + title,
        loc.format(2, 2) + '',
        loc.format(3, 2) + head,
        loc.format(4, 2) + frame,
        loc.format(5, 1) + row.format(*data[0]),
        loc.format(6, 1) + row.format(*data[1]),
        loc.format(7, 1) + frame,
        loc.format(8, 2) + fmt.format('spam'),
        loc.format(8, 2) + fmt.format(''),
    ]) + '\n'
    assert returned == 'x'


@pytest.mark.msg(('input', 'spam',), [
    Keystroke('\x1b'),
    'x',
    'n',
])
def test_Table_input_esc_to_help(table_input_test):
    """When called with a prompt, :meth:`blackjack.termui.Table.input`
    should write the prompt to the UI and return the response from
    the user. The ESC key should send the user to the help screen.
    """
    displayed, returned = table_input_test
    assert displayed == '\n'.join([
        loc.format(8, 2) + fmt.format('spam'),
        loc.format(8, 2) + fmt.format(''),
        home + cls,
        topleft + bold + title,
        loc.format(2, 2) + '',
        loc.format(3, 2) + head,
        loc.format(4, 2) + frame,
        loc.format(5, 1) + row.format(*data[0]),
        loc.format(6, 1) + row.format(*data[1]),
        loc.format(7, 1) + frame,
        loc.format(8, 2) + fmt.format('spam'),
        loc.format(8, 2) + fmt.format(''),
    ]) + '\n'
    assert returned == 'x'


# Test for Table.input_multichar.
@pytest.mark.msg(('input_multichar', 'spam',), ['2', '0', '\n',])
def test_Table_input_multichar(table_input_test):
    """When called with a prompt,
    :meth:`blackjack.termui.Table.input_multichar'
    should write the prompt to the UI and return the
    response from the user.
    """
    displayed, returned = table_input_test
    assert displayed == '\n'.join([
        loc.format(8, 2) + fmt.format('spam' + ' > '),
        loc.format(8, 7) + '2',
        loc.format(8, 8) + '0',
        loc.format(8, 2) + fmt.format(''),
    ]) + '\n'
    assert returned == '20'


@pytest.mark.msg(('input_multichar', 'spam', '20'), ['\n',])
def test_Table_input_multichar_default(table_input_test):
    """When called with a prompt,
    :meth:`blackjack.termui.Table.input_multichar'
    should write the prompt to the UI and return the
    response from the user.
    """
    displayed, returned = table_input_test
    assert displayed == '\n'.join([
        loc.format(8, 2) + fmt.format('spam' + ' > '),
        loc.format(8, 2) + fmt.format(''),
    ]) + '\n'
    assert returned == '20'


@pytest.mark.msg(('input_multichar', 'spam',), [
    Keystroke('\x1b'),
    'x',
    '2',
    '0',
    '\n',
])
def test_Table_input_multichar_esc_to_help(table_input_test):
    """When called with a prompt,
    :meth:`blackjack.termui.Table.input_multichar'
    should write the prompt to the UI and return the
    response from the user. When the user presses
    the escape key, the help screen should be invoked.
    """
    displayed, returned = table_input_test
    assert displayed == '\n'.join([
        loc.format(8, 2) + fmt.format('spam' + ' > '),
        home + cls,
        loc.format(1, 1) + fmt.format(''),
        loc.format(2, 1) + fmt.format(''),
        loc.format(3, 1) + fmt.format(''),
        loc.format(4, 1) + fmt.format(''),
        loc.format(5, 1) + fmt.format(''),
        loc.format(6, 1) + fmt.format(''),
        loc.format(7, 1) + fmt.format(''),
        loc.format(8, 1) + fmt.format(''),
        topleft + bold + title,
        loc.format(2, 2) + '',
        loc.format(3, 2) + head,
        loc.format(4, 2) + frame,
        loc.format(5, 1) + row.format(*data[0]),
        loc.format(6, 1) + row.format(*data[1]),
        loc.format(7, 1) + frame,
        loc.format(8, 2) + fmt.format('spam > '),
        loc.format(8, 7) + 'x',
        loc.format(8, 8) + '2',
        loc.format(8, 9) + '0',
        loc.format(8, 2) + fmt.format(''),
    ]) + '\n'
    assert returned == 'x20'


@pytest.mark.msg(('input_multichar', 'spam',), ['2', '0', '\n',])
def test_Table_input_multichar_with_status(table_input_with_status_test):
    """When called with a prompt,
    :meth:`blackjack.termui.Table.input_multichar'
    should write the prompt to the UI and return the
    response from the user.
    """
    displayed, returned = table_input_with_status_test
    assert displayed == '\n'.join([
        loc.format(10, 2) + fmt.format('spam' + ' > '),
        loc.format(10, 7) + '2',
        loc.format(10, 8) + '0',
        loc.format(10, 2) + fmt.format(''),
    ]) + '\n'
    assert returned == '20'


# Tests for Table.update.
@pytest.mark.msg(('update', [[1, 2], [3, 'spam']],))
def test_Table_update(table_draw_test):
    """When called with a message, :meth:`blackjack.termui.Table.update`
    should update the changed data in the table.
    """
    assert table_draw_test == (
        loc.format(6, 13)
        + fields[1][1].format('spam')
        + '\n'
    )


@pytest.mark.msg(('update', [[1, 2], [3, 4], [5, 6],],))
def test_Table_update_bigger_table(table_draw_test):
    """When called with a message, :meth:`blackjack.termui.Table.update`
    should update the changed data in the table.
    """
    actual = table_draw_test
    expected = '\n'.join([
        loc.format(8, 1) + ' ' * 80,
        loc.format(7, 1) + ' ' * 80,
        loc.format(8, 1) + frame,
        loc.format(7, 2) + fields[0][1].format('5'),
        loc.format(7, 13) + fields[1][1].format('6'),
    ]) + '\n'
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


@pytest.mark.msg(('update', [[1, 2], [3, 4], [5, 6],],))
def test_Table_update_bigger_table_with_status(table_draw_with_status_test):
    """When called with a message, :meth:`blackjack.termui.Table.update`
    should update the changed data in the table.
    """
    actual = table_draw_with_status_test
    expected = '\n'.join([
        loc.format(10, 1) + ' ' * 80,
        loc.format(9, 1) + ' ' * 80,
        loc.format(8, 1) + ' ' * 80,
        loc.format(7, 1) + ' ' * 80,
        loc.format(8, 1) + frame,
        loc.format(9, 1) + ' ' * 80,
        loc.format(9, 2) + 'Count: 0',
        loc.format(10, 1) + frame,
        loc.format(7, 2) + fields[0][1].format('5'),
        loc.format(7, 13) + fields[1][1].format('6'),
    ]) + '\n'
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


@pytest.mark.msg(('update', [[1, 2],],))
def test_Table_update_smaller_table(table_draw_test):
    """When called with a message, :meth:`blackjack.termui.Table.update`
    should update the changed data in the table.
    """
    assert table_draw_test == '\n'.join([
        loc.format(8, 1) + ' ' * 80,
        loc.format(7, 1) + ' ' * 80,
        loc.format(6, 1) + frame,
    ]) + '\n'


@pytest.mark.msg(('update', [[1, 2],],))
def test_Table_update_smaller_table_with_status(table_draw_with_status_test):
    """When called with a message, :meth:`blackjack.termui.Table.update`
    should update the changed data in the table.
    """
    # raise ValueError(table_draw_with_status_test)
    act = table_draw_with_status_test
    exp = '\n'.join([
        loc.format(10, 1) + ' ' * 80,
        loc.format(9, 1) + ' ' * 80,
        loc.format(8, 1) + ' ' * 80,
        loc.format(7, 1) + ' ' * 80,
        loc.format(6, 1) + frame,
        loc.format(7, 1) + ' ' * 80,
        loc.format(7, 2) + 'Count: 0',
        loc.format(8, 1) + frame,
    ]) + '\n'
    try:
        assert act == exp
    except AssertionError:
        raise AssertionError(repr(act) + ' == ' + repr(exp))


# Tests for Table.update_status.
@pytest.mark.msg(('update_status', {'Count': '9',},))
def test_Table_update_status(table_draw_with_status_test):
    """When called with a message,
    :meth:`blackjack.termui.Table.update_status`
    should update the status.
    """
    assert table_draw_with_status_test == '\n'.join([
        loc.format(8, 1) + ' ' * 80,
        loc.format(8, 2) + f'Count: 9',
        loc.format(9, 1) + frame,
    ]) + '\n'


# Tests for TableUI.
# TableUI fixtures.
@pytest.fixture
def tableui_with_mocked_main(mocker):
    """A default :class:`blackjack.termui.TableUI` object."""
    mock_main = mocker.patch('blackjack.termui.main')
    ui = termui.TableUI()
    ui.ctlr.data = [[players.Player(name='spam', chips=80), 100, '', '', ''],]
    ui.start()
    yield ui, mock_main
    ui.end()


@pytest.fixture
def tableui_with_mocked_main_and_two_players(mocker):
    """A default :class:`blackjack.termui.TableUI` object."""
    mock_main = mocker.patch('blackjack.termui.main')
    ui = termui.TableUI()
    ui.ctlr.data = [
        [
            players.Player(
                [
                    cards.Hand([cards.Card(11, 0),]),
                    cards.Hand([cards.Card(11, 3),]),
                ],
                name='spam', chips=80
            ),
            100, 20, 'J♣ J♠', 'Takes hand.'
        ],
        [
            players.Player(
                [cards.Hand([cards.Card(3, 3), cards.Card(4, 3),]),],
                name='eggs', chips=80
            ),
            100, 20, '3♣ 4♣', 'Takes hand.'
        ],
    ]
    ui.start()
    yield ui, mock_main
    ui.end()


@pytest.fixture
def tableui_with_mocked_bet(mocker):
    """A default :class:`blackjack.termui.TableUI` object."""
    mock_bet = mocker.patch('blackjack.termui.TableUI._update_bet')
    ui = termui.TableUI()
    ui.ctlr.data = [[players.Player(name='spam', chips=80), 80, 20, '', ''],]
    ui.start()
    yield ui, mock_bet
    ui.end()


@pytest.fixture
def tableui_with_mocked_event(mocker):
    """A default :class:`blackjack.termui.TableUI` object."""
    mock_event = mocker.patch('blackjack.termui.TableUI._update_event')
    ui = termui.TableUI()
    ui.ctlr.data = [[players.Player(name='spam', chips=80), 80, 20, '', ''],]
    ui.start()
    yield ui, mock_event
    ui.end()


@pytest.fixture
def tableui_with_mocked_hand(mocker):
    """A default :class:`blackjack.termui.TableUI` object."""
    mock_hand = mocker.patch('blackjack.termui.TableUI._update_hand')
    ui = termui.TableUI()
    ui.ctlr.data = [[players.Player(name='spam', chips=80), 80, 20, '', ''],]
    ui.start()
    yield ui, mock_hand
    ui.end()


# Tests for TableUI initialization.
def test_TableUI_init():
    """On initialization, :class:`TableUI` should not require optional
    attributes.
    """
    ui = termui.TableUI()
    assert isinstance(ui.ctlr, termui.Table)


def test_TableUI_init_optional_attrs():
    """On initialization, :class:`TableUI` should accept optional
    attributes.
    """
    expected = {
        'ctlr': termui.Table('Spam', (
            termui.Field('Eggs', '{}'),
            termui.Field('Baked Beans', '{}'),
        )),
        'seats': 6,
        'show_status': False,
    }
    ui = termui.TableUI(**expected)

    for attr in expected:
        try:
            a = getattr(ui, attr)
            e = expected[attr]
            assert a == e
        except AssertionError:
            raise AssertionError(f'{attr} {a} == {e}')


def test_TableUI_init_show_status_Table_with_status():
    """On initialization, :class:`TableUI` should accept optional
    attributes. If :attr:`TableUI.show_status` is initialized as
    `True` the value of :attr:`TableUI.ctlr` should have a `show_status`
    also equal to `True`.
    """
    ui = termui.TableUI(show_status=True)
    assert ui.ctlr.show_status


# Tests for TableUI loop management.
def test_TableUI_end(mocker):
    """When called, :meth:`blackjack.termui.TableUI.end` should
    terminate UI loop gracefully.
    """
    mock_main = mocker.patch('blackjack.termui.main')

    ui = termui.TableUI()
    ui.start()

    ui.end()
    assert mock_main.mock_calls[-1] == mocker.call().close()


def test_TableUI_reset(mocker):
    """When called, :meth:`blackjack.termui.TableUI.reset` should
    terminate the existing controller, create a new one, and prime it.
    """
    mock_main = mocker.patch('blackjack.termui.main')

    ui = termui.TableUI()
    ui.start()

    ui.reset()
    assert mock_main.mock_calls[-4:] == [
        mocker.call().close(),
        mocker.call(ui.ctlr, False, ''),
        mocker.call().__next__(),
        mocker.call().send(('draw',)),
    ]

    ui.end()


def test_TableUI_start(mocker):
    """When called, :meth:`blackjack.termui.TableUI.start` should
    kick off the main loop of the UI, set it as the loop attribute,
    and prime it.
    """
    mock_main = mocker.patch('blackjack.termui.main')

    ui = termui.TableUI()

    ui.start()
    assert mock_main.mock_calls == [
        mocker.call(ui.ctlr, False, ''),
        mocker.call().__next__(),
        mocker.call().send(('draw',)),
    ]

    ui.end()


# Tests for TableUI private update methods.
def test_TableUI__update_bet(mocker, tableui_with_mocked_main):
    """Given a player, a bet amount, and a message,
    :meth:`blackjack.termui.TableUI._update_bet` should
    send an event to the UI that a player's bet has
    changed.
    """
    tableui, mock_main = tableui_with_mocked_main
    player = tableui.ctlr.data[0][0]
    msg = 'Bets.'

    try:
        tableui._update_bet(player, 20, msg)
        actual = mock_main.mock_calls[-1]
        expected = mocker.call().send((
            'update',
            [[player, 80, 20, '', msg]]
        ))
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


def test_TableUI__update_event(mocker, tableui_with_mocked_main):
    """Given a player and a event,
    :meth:`blackjack.termui.TableUI._update_event` should
    send an event to the UI that a game event has occurred.
    """
    tableui, mock_main = tableui_with_mocked_main
    player = tableui.ctlr.data[0][0]
    event = 'Shuffles the deck.'

    try:
        tableui._update_event(player, event)
        actual = mock_main.mock_calls[-1]
        expected = mocker.call().send((
            'update',
            [[player, 100, '', '', event]]
        ))
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


def test_TableUI__update_hand(mocker, tableui_with_mocked_main):
    """Given a player, a hand, and a message,
    :meth:`blackjack.termui.TableUI._update_hand` should
    send an event to the UI that a player's hand has
    changed.
    """
    hand = cards.Hand((cards.Card(11, 0), cards.Card(5, 2),))
    tableui, mock_main = tableui_with_mocked_main
    player = tableui.ctlr.data[0][0]
    msg = 'Takes hand.'

    try:
        tableui._update_hand(player, hand, msg)
        actual = mock_main.mock_calls[-1]
        expected = mocker.call().send((
            'update',
            [[player, 100, '', str(hand), msg]]
        ))
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


# Tests for TableUI public update methods.
def test_TableUI_bet_updates(mocker, tableui_with_mocked_bet):
    """The tested methods should call the
    :meth:`backjack.TableUI.termui._update_bet`
    method with the player, bet, and event text.
    """
    ui, mock_bet = tableui_with_mocked_bet
    player = ui.ctlr.data[0][0]
    bet = 20
    expected = [
        mocker.call(player, bet, 'Bets.'),
        mocker.call(player, bet, 'Doubles down.'),
        mocker.call(player, bet, f'Buys {bet} insurance.'),
        mocker.call(player, bet, f'Insurance pays {bet}.'),
        mocker.call(player, '', 'Loses.'),
        mocker.call(player, '', 'Loses.', True),
        mocker.call(player, '', f'Ties {bet}.'),
        mocker.call(player, '', f'Wins {bet}.'),
        mocker.call(player, '', f'Ties {bet}.', True),
        mocker.call(player, '', f'Wins {bet}.', True),
    ]

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
    actual = mock_bet.mock_calls[-10:]
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


def test_TableUI_event_updates(mocker, tableui_with_mocked_event):
    """The tested methods should call the
    :meth:`backjack.TableUI.termui._update_event`
    method with the player, bet, and event text.
    """
    ui, mock_event = tableui_with_mocked_event
    player = ui.ctlr.data[0][0]
    event = 'Shuffles the deck.'
    expected = [
        mocker.call(player, event),
    ]

    ui.shuffles(player)
    actual = mock_event.mock_calls[-1:]
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


def test_TableUI_hand_updates(mocker, tableui_with_mocked_hand):
    """The tested methods should call the
    :meth:`backjack.TableUI.termui._update_hand`
    method with the player, hand, and event text.
    """
    ui, mock_hand = tableui_with_mocked_hand
    player = ui.ctlr.data[0][0]
    hand = cards.Hand([
        cards.Card(11, 0),
        cards.Card(10, 3),
    ])
    expected = [
        mocker.call(player, hand, 'Takes hand.'),
        mocker.call(player, hand, 'Flips card.'),
        mocker.call(player, hand, 'Hits.'),
        mocker.call(player, hand, 'Stands.'),
    ]

    ui.deal(player, hand)
    ui.flip(player, hand)
    ui.hit(player, hand)
    ui.stand(player, hand)
    actual = mock_hand.mock_calls[-4:]
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


def test_TableUI_splits(mocker, tableui_with_mocked_main_and_two_players):
    """When given a player and a bet, :meth:`blackjack.termui.TableUI.splits`
    should add a row to the data table for the split hand, update it with
    the relevant information, and send it to the UI.
    """
    tableui, mock_main = tableui_with_mocked_main_and_two_players
    data = tableui.ctlr.data
    player = data[0][0]
    expected = [
        mocker.call().send(('update', [
            [player, 80, 20, 'J♣', 'Splits hand.'],
            ['  \u2514\u2500', '', 20, 'J♠', ''],
            data[1],
        ])),
    ]

    tableui.splits(player, 20)
    actual = mock_main.mock_calls[-1:]
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


class TableUITestCase(ut.TestCase):
    # Update method tests.
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
        ui = termui.TableUI()
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
        ui = termui.TableUI()
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
        ui = termui.TableUI()
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
        ui = termui.TableUI()
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
        ui = termui.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.cleanup()
        act = mock_main.mock_calls[-1]

        self.assertEqual(exp, act)

    # Input method tests.
    @patch('blackjack.termui.Table.input_multichar', return_value='300')
    def test_bet_prompt(self, mock_input):
        """When called, _multichar_prompt() should send the UI a
        prompt for user input and return the result.
        """
        # Expected value.
        bet_min = 20
        bet_max = 500
        exp_value = model.Bet(mock_input())
        exp_call = call(
            f'How much do you wish to bet? [{bet_min}-{bet_max}]',
            '20'
        )

        # Test data and state.
        ui = termui.TableUI()
        ui.start()

        # Run test and gather actuals.
        act_value = ui.bet_prompt(bet_min, bet_max)
        act_call = mock_input.mock_calls[-1]

        # Test clean up.
        ui.end()

        # Determine test results.
        self.assertEqual(exp_value, act_value)
        self.assertEqual(exp_call, act_call)

    @patch('blackjack.termui.Table.error')
    @patch('blackjack.termui.Table.input_multichar')
    def test_bet_prompt_handle_invalid(self, mock_input, mock_error):
        """When called, _multichar_prompt() should send the UI a
        prompt for user input and return the result.
        """
        # Expected value.
        bet_min = 20
        bet_max = bet_min + 100
        exp_value = model.Bet(bet_min + 10)
        exp_calls = [
            call(f'How much do you wish to bet? [{bet_min}-{bet_max}]', '20'),
            call(f'How much do you wish to bet? [{bet_min}-{bet_max}]', '20'),
            call(f'How much do you wish to bet? [{bet_min}-{bet_max}]', '20'),
            call('Invalid response.'),
            call('Invalid response.'),
            call(''),
        ]

        # Test data and state.
        mock_input.side_effect = [
            'f',
            f'{bet_max + 10}',
            f'{exp_value.value}',
        ]
        ui = termui.TableUI()
        ui.start()

        # Run test and gather actuals.
        act_value = ui.bet_prompt(bet_min, bet_max)
        act_calls = mock_input.mock_calls
        act_calls.extend(mock_error.mock_calls)

        # Test clean up.
        ui.end()

        # Determine test results.
        self.assertEqual(exp_value, act_value)
        self.assertListEqual(exp_calls, act_calls)

    @patch('blackjack.termui.Table.input_multichar', return_value='300')
    def test_insure_prompt(self, mock_input):
        """When called, insure_prompt() should send the UI a
        prompt the user for an insurance about and return the result.
        """
        # Expected value.
        insure_max = 500
        exp_value = model.Bet(mock_input())
        exp_call = call(
            f'How much insurance do you want? [0-{insure_max}]',
            '0'
        )

        # Test data and state.
        ui = termui.TableUI()
        ui.start()

        # Run test and gather actuals.
        act_value = ui.insure_prompt(insure_max)
        act_call = mock_input.mock_calls[-1]

        # Test clean up.
        ui.end()

        # Determine test results.
        self.assertEqual(exp_value, act_value)
        self.assertEqual(exp_call, act_call)

    @patch('blackjack.termui.Table.error')
    @patch('blackjack.termui.Table.input_multichar')
    def test_insure_prompt_handle_invalid(self, mock_input, mock_error):
        """When called, insure_prompt() should send the UI a
        prompt the user for an insurance about and return the result.
        """
        # Expected value.
        insure_max = 500
        exp_value = model.Bet(insure_max - 1)
        exp_calls = [
            call(f'How much insurance do you want? [0-{insure_max}]', '0'),
            call(f'How much insurance do you want? [0-{insure_max}]', '0'),
            call(f'How much insurance do you want? [0-{insure_max}]', '0'),
            call('Invalid response.'),
            call('Invalid response.'),
            call(''),
        ]

        # Test data and state.
        mock_input.side_effect = ('f', f'{insure_max + 1}', exp_value.value)
        ui = termui.TableUI()
        ui.start()

        # Run test and gather actuals.
        act_value = ui.insure_prompt(insure_max)
        act_calls = mock_input.mock_calls
        act_calls.extend(mock_error.mock_calls)

        # Test clean up.
        ui.end()

        # Determine test results.
        self.assertEqual(exp_value, act_value)
        self.assertListEqual(exp_calls, act_calls)

    @patch('blackjack.termui.main')
    def test___prompt_calls(self, mock_main):
        """When called, _prompt() should send the UI a prompt for user
        input and return the result.
        """
        exp_call = call().send(('input', 'spam', 'y'))

        ui = termui.TableUI()
        ui.start()
        act_resp = ui._prompt('spam', 'y')
        act_call = mock_main.mock_calls[-1]
        ui.end()

        self.assertEqual(exp_call, act_call)

    @patch('blackjack.termui.main')
    @patch('blackjack.termui.TableUI._prompt')
    def test__yesno_prompt(self, mock_prompt, _):
        """When called, _multichar_prompt() should prompt the user
        for an answer. The response should be returned.
        """
        exp_resp = model.IsYes('y')
        exp_call = call('Play another round? [yn] > ', 'y')

        ui = termui.TableUI()
        mock_prompt.return_value = 'y'
        ui.start()
        act_resp = ui._yesno_prompt('Play another round?', 'y')
        ui.end()
        act_call = mock_prompt.mock_calls[-1]

        self.assertEqual(exp_resp.value, act_resp.value)
        self.assertEqual(exp_call, act_call)

    @patch('blackjack.termui.Table.error')
    @patch('blackjack.termui.Table.input')
    def test__yesno_prompt_handle_invalid(self, mock_input, mock_error):
        """When called, _yesno_prompt() should prompt the user
        for a yes/no answer. The response should be returned.
        """
        # Expected value.
        exp_resp = model.IsYes('y')
        exp_calls = [
            call('Play another round? [yn] > ', 'y'),
            call('Play another round? [yn] > ', 'y'),
            call('Play another round? [yn] > ', 'y'),
            call('Invalid response.'),
            call('Invalid response.'),
            call(''),
        ]

        # Test data and state.
        ui = termui.TableUI()
        mock_input.side_effect = ('6', 'f', exp_resp.value)
        ui.start()

        # Run test.
        act_resp = ui._yesno_prompt('Play another round?', 'y')

        # Cleanup state and gather actuals.
        ui.end()
        act_calls = mock_input.mock_calls
        act_calls.extend(mock_error.mock_calls)

        # Determine test results.
        self.assertEqual(exp_resp, act_resp)
        self.assertListEqual(exp_calls, act_calls)

    @patch('blackjack.termui.Table.input')
    def test__yesno_prompt_until_valid(self, mock_main):
        """If the user responds with an invalid value, the prompt
        should be repeated.
        """
        exp_resp = model.IsYes('n')

        ui = termui.TableUI()
        mock_main.side_effect = [None, None, 'z', ' ', 'n']
        ui.start()
        act_resp = ui._yesno_prompt('spam', 'y')
        ui.end()

        self.assertEqual(exp_resp.value, act_resp.value)

    @patch('blackjack.termui.main')
    @patch('blackjack.termui.TableUI._yesno_prompt')
    def test__yesnos(self, mock_yesno, _):
        """The individual yes/no prompts should sent their prompt and
        a default response value to _yesno_prompt and return the
        response.
        """
        exp_resp = model.IsYes('y')
        exp_calls = [
            call('Double down?', 'y'),
            call('Hit?', 'y'),
            call('Play another round?', 'y'),
            call('Split your hand?', 'y'),
        ]

        mock_yesno.return_value = exp_resp
        ui = termui.TableUI()
        ui.start()
        act_resps = []
        act_resps.append(ui.doubledown_prompt())
        act_resps.append(ui.hit_prompt())
        act_resps.append(ui.nextgame_prompt())
        act_resps.append(ui.split_prompt())
        act_calls = mock_yesno.mock_calls[-5:]
        ui.end()

        for act_resp in act_resps:
            self.assertEqual(exp_resp, act_resp)
        for exp, act in zip(exp_calls, act_calls):
            self.assertEqual(exp, act)

    # Update count tests.
    @patch('blackjack.termui.main')
    def test_update_count(self, mock_main):
        """When called, update the running count in the UI."""
        # Expected value.
        status = {
            'Count': '2',
        }
        exp = call().send(('update_status', status))

        # Test data and state.
        player = players.Player(name='spam', chips=80)
        data = [[player, 80, '', '', ''],]
        ui = termui.TableUI()
        ui.ctlr.data = data
        ui.start()

        # Run test.
        ui.update_count(status['Count'])

        # Gather actual
        act = mock_main.mock_calls[-1]
        ui.end()

        # Determine test result.
        self.assertEqual(exp, act)


# Tests for main.
class mainTestCase(ut.TestCase):
    def test_init_with_params(self):
        """main() should create its own instances of term and ctlr if
        none are supplied.
        """
        ctlr = model.TerminalController()
        main = termui.main(ctlr)

        # This will fail the test due to a exception if
        # ctlr.term.fullscreen cannot be called.
        next(main)

    def test_init_no_params(self):
        """main() should create its own TerminalController if one is
        not passed.
        """
        main = termui.main()

        # This will fail the test due to a exception if
        # ctlr.term.fullscreen cannot be called.
        next(main)

    @patch('blessed.Terminal')
    def test_terminate(self, _):
        """When StopGeneration is raised to main(), main should
        terminate gracefully.
        """
        exp = StopIteration

        main = termui.main()
        next(main)
        main.close()

        with self.assertRaises(exp):
            _ = main.send(('draw',))
