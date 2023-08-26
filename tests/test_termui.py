"""
test_termui.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.termui module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import pytest
from blessed import Terminal
from blessed.keyboard import Keystroke

from blackjack import cards, game, model, players, termui


# Common ANSI escape sequences.
bold = '\x1b[1m'
cls = '\x1b[2J'
home = '\x1b[H'
loc = '\x1b[{};{}H'
topleft = '\x1b[1;2H'


# Utility functions.
def catch_failure(actual, expected):
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


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


# Tests for main.
def test_main_with_params():
    """:func:`blackjack.termui.main` should create its own instances
    of term and ctlr if none are supplied. This test will fail with
    an exception if `ctlr.term.fullscreen` cannot be called.
    """
    ctlr = model.TerminalController()
    main = termui.main(ctlr)
    next(main)


def test_main_without_params():
    """:func:`blackjack.termui.main` should create its own instance
    of :class:`blackjack.model.TerminalController` if one is not
    supplied. This test will fail with an exception if
    `ctlr.term.fullscreen` cannot be called.
    """
    main = termui.main()
    next(main)


def test_terminate(mocker):
    """After being ended, :func:`blackjack.termui.main` should raise
    a :class:`StopIteration` exception if any messages are sent to it.
    """
    mocker.patch('blessed.Terminal')
    main = termui.main()
    next(main)
    main.close()
    with pytest.raises(StopIteration):
        _ = main.send(('draw',))


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
# Common data for Table.
data = [[1, 2], [3, 4]]
fields = [
    ('Name', '{:>10}'),
    ('Value', '{:>10}'),
]
fmt = '{:<80}'
frame = '\u2500' * 23
head = ' ' + ' '.join('{:<10}'.format(f[0]) for f in fields)
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


@pytest.fixture
def tableui_with_mocked_input(mocker):
    """A default :class:`blackjack.termui.TableUI` object."""
    mock_input = mocker.patch('blackjack.termui.Table.input')
    mock_error = mocker.patch('blackjack.termui.Table.error')
    ui = termui.TableUI()
    ui.ctlr.data = [[players.Player(name='spam', chips=80), 100, '', '', ''],]
    ui.start()
    yield ui, mock_input, mock_error
    ui.end()


@pytest.fixture
def tableui_with_mocked_input_multichar(mocker):
    """A default :class:`blackjack.termui.TableUI` object."""
    mock_input = mocker.patch('blackjack.termui.Table.input_multichar')
    mock_error = mocker.patch('blackjack.termui.Table.error')
    ui = termui.TableUI()
    ui.ctlr.data = [[players.Player(name='spam', chips=80), 100, '', '', ''],]
    ui.start()
    yield ui, mock_input, mock_error
    ui.end()


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
def tableui_with_mocked_main_and_split(mocker):
    """A default :class:`blackjack.termui.TableUI` object."""
    mock_main = mocker.patch('blackjack.termui.main')
    ui = termui.TableUI()
    ui.ctlr.data = [
        [players.Player([
            cards.Hand([cards.Card(11, 0),]),
            cards.Hand([cards.Card(11, 3),]),
        ], name='spam', chips=80), 80, 20, 'J♣', ''],
        ['  \u2514\u2500', '', 20, 'J♠', ''],
    ]
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
def tableui_with_mocked_yesno(mocker):
    """A default :class:`blackjack.termui.TableUI` object."""
    mock_yesno = mocker.patch('blackjack.termui.TableUI._yesno_prompt')
    ui = termui.TableUI()
    ui.ctlr.data = [[players.Player(name='spam', chips=80), 100, '', '', ''],]
    ui.start()
    yield ui, mock_yesno
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


def test_TableUI__update_bet_split(
    mocker,
    tableui_with_mocked_main_and_split
):
    """Given a player, a bet amount, and a message,
    :meth:`blackjack.termui.TableUI._update_bet` should
    send an event to the UI that a player's bet has
    changed.
    """
    tableui, mock_main = tableui_with_mocked_main_and_split
    data = tableui.ctlr.data[:]
    data[1][4] = 'Loses.'
    player = data[0][0]
    expected = [mocker.call().send(('update', data))]

    tableui._update_bet(player, 20, 'Loses.', split=True)
    actual = mock_main.mock_calls[-1:]
    try:
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


def test_TableUI__update_hand_split(
    mocker,
    tableui_with_mocked_main_and_split
):
    """If sent a split hand, :meth:`blackjack.termui.TableUI._update_hand`
    should update the split row of the table.
    """
    tableui, mock_main = tableui_with_mocked_main_and_split
    data = tableui.ctlr.data[:]
    expected = [
        mocker.call().send(('update', [
            data[0],
            [
                data[1][0],
                data[1][1],
                data[1][2],
                data[1][3] + ' 5♣',
                'Hits.',
            ]
        ])),
    ]

    player = data[0][0]
    player.hands[1].append(cards.Card(5, 0))
    tableui._update_hand(player, player.hands[1], 'Hits.')
    actual = mock_main.mock_calls[-1:]
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


# Tests for TableUI public update methods.
def test_TableUI_all_bet_updates(mocker, tableui_with_mocked_bet):
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


def test_TableUI_all_event_updates(mocker, tableui_with_mocked_event):
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


def test_TableUI_all_hand_updates(mocker, tableui_with_mocked_hand):
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


def test_TableUI_cleanup(mocker, tableui_with_mocked_main_and_two_players):
    """When called, :meth:`blackjack.termui.TableUI.cleanup` should add
    clear the bet, hand, and event field of every row in the data table,
    then send it to the UI.
    """
    tableui, mock_main = tableui_with_mocked_main_and_two_players
    data = tableui.ctlr.data[:]
    player1 = data[0][0]
    player2 = data[1][0]
    new_data = [
        [player1, 80, '', '', ''],
        [player2, 80, '', '', ''],
    ]
    expected = [
        mocker.call().send(('update', new_data)),
    ]

    tableui.cleanup()
    actual = mock_main.mock_calls[-1:]
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


def test_TableUI_joins(mocker, tableui_with_mocked_main_and_two_players):
    """When given a player, :meth:`blackjack.termui.TableUI.joins`
    should add the player to the data table in the first empty row.
    """
    tableui, mock_main = tableui_with_mocked_main_and_two_players
    tableui.ctlr.data[1] = ['', '', '', '', '']
    player = players.Player(name='eggs', chips=100)
    expected = [mocker.call().send(('update', [
        tableui.ctlr.data[0],
        [player, 100, '', '', 'Sits down.'],
    ])),]

    tableui.joins(player)
    actual = mock_main.mock_calls[-1:]
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')


def test_TableUI_leaves(mocker, tableui_with_mocked_main_and_two_players):
    """When given a player, :meth:`blackjack.termui.TableUI.leaves`
    should announce the player is leaving and remove the player from
    the data table. In order to avoid the row in the UI just going
    blank, this call will edit self.ctlr.data directly.
    """
    tableui, mock_main = tableui_with_mocked_main_and_two_players
    data = tableui.ctlr.data
    player = data[0][0]
    expected = [
        mocker.call().send(('update', [
            [player, '', '', '', 'Walks away.'],
            data[1],
        ])),
    ]

    tableui.leaves(player)
    actual = mock_main.mock_calls[-1:]
    try:
        assert actual == expected
    except AssertionError:
        raise AssertionError(f'{actual!r} == {expected!r}')

    actual = tableui.ctlr.data
    expected = [
        ['', 100, 20, 'J♣ J♠', 'Takes hand.'],
        data[1],
    ]
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


# Tests for TableUI multi-character input methods.
def test_TableUI_bet_prompt(mocker, tableui_with_mocked_input_multichar):
    """When called, :meth:`blackjack.termui.TableUI.bet_prompt should
    send a call to the UI to prompt for user input and return the result.
    """
    ui, mock_input, mock_error = tableui_with_mocked_input_multichar
    mock_input.return_value = '300'
    assert ui.bet_prompt(20, 500) == model.Bet('300')
    assert mock_input.mock_calls[-1:] == [mocker.call(
        'How much do you wish to bet? [20-500]',
        '20'
    )]


def test_TableUI_bet_prompt_invalid(
    mocker,
    tableui_with_mocked_input_multichar,
):
    """When called, :meth:`blackjack.termui.TableUI.bet_prompt` should
    a call to the UI to prompt for user input and return the result.
    If input from the user is invalid, continue to prompt until the
    user inputs a valid value.
    """
    ui, mock_input, mock_error = tableui_with_mocked_input_multichar
    mock_input.side_effect = ['f', '510', '30']

    catch_failure(ui.bet_prompt(20, 500), model.Bet('30'))
    catch_failure(mock_input.mock_calls[-3:], [
        mocker.call('How much do you wish to bet? [20-500]', '20'),
        mocker.call('How much do you wish to bet? [20-500]', '20'),
        mocker.call('How much do you wish to bet? [20-500]', '20'),
    ])
    catch_failure(mock_error.mock_calls[-3:], [
        mocker.call('Invalid response.'),
        mocker.call('Invalid response.'),
        mocker.call(''),
    ])


def test_TableUI_insure_prompt(mocker, tableui_with_mocked_input_multichar):
    """When called, :meth:`blackjack.termui.TableUI.insure_prompt should
    send a call to the UI to prompt the user for an insurance decision
    and return the result.
    """
    ui, mock_input, mock_error = tableui_with_mocked_input_multichar
    mock_input.return_value = '300'
    assert ui.insure_prompt(500) == model.Bet('300')
    assert mock_input.mock_calls[-1:] == [mocker.call(
        'How much insurance do you want? [0-500]',
        '0'
    )]


def test_TableUI_insure_prompt_invalid(
    mocker,
    tableui_with_mocked_input_multichar,
):
    """When called, :meth:`blackjack.termui.TableUI.bet_insure` should
    send a call to the UI to prompt for user input and return the result.
    If input from the user is invalid, continue to prompt until the
    user inputs a valid value.
    """
    ui, mock_input, mock_error = tableui_with_mocked_input_multichar
    mock_input.side_effect = ['f', '510', '30']

    catch_failure(ui.insure_prompt(500), model.Bet('30'))
    catch_failure(mock_input.mock_calls[-3:], [
        mocker.call('How much insurance do you want? [0-500]', '0'),
        mocker.call('How much insurance do you want? [0-500]', '0'),
        mocker.call('How much insurance do you want? [0-500]', '0'),
    ])
    catch_failure(mock_error.mock_calls[-3:], [
        mocker.call('Invalid response.'),
        mocker.call('Invalid response.'),
        mocker.call(''),
    ])


# Tests for TableUI private single character input methods.
def test_TableUI__prompt(mocker, tableui_with_mocked_main):
    """When called, :meth:`blackjack.termui.TableUI._prompt() should
    send the UI a prompt for user input and return the result.
    """
    ui, mock_main = tableui_with_mocked_main
    ui._prompt('spam', 'y')
    catch_failure(mock_main.mock_calls[-1:], [
        mocker.call().send(('input', 'spam', 'y'))
    ])


def test_TableUI__yesno_prompt(mocker, tableui_with_mocked_input):
    """When called, :meth:`blackjack.termui.TableUI._yesno_prompt` should
    send a call to the UI to prompt for user input and return the result.
    """
    ui, mock_input, mock_error = tableui_with_mocked_input
    mock_input.return_value = 'n'
    assert ui._yesno_prompt('Spam?', 'y') == model.IsYes('n')
    assert mock_input.mock_calls[-1:] == [mocker.call('Spam? [yn] > ', 'y')]


def test_TableUI__yesno_prompt_invalid(mocker, tableui_with_mocked_input):
    """When called, :meth:`blackjack.termui.TableUI._yesno_prompt` should
    send a call to the UI to prompt for user input and return the result.
    If input from the user is invalid, continue to prompt until the user
    inputs a valid value.
    """
    ui, mock_input, mock_error = tableui_with_mocked_input
    mock_input.side_effect = ['f', '6', 'y']

    catch_failure(ui._yesno_prompt('Spam?', 'y'), model.IsYes('y'))
    catch_failure(mock_input.mock_calls[-3:], [
        mocker.call('Spam? [yn] > ', 'y'),
        mocker.call('Spam? [yn] > ', 'y'),
        mocker.call('Spam? [yn] > ', 'y'),
    ])
    catch_failure(mock_error.mock_calls[-3:], [
        mocker.call('Invalid response.'),
        mocker.call('Invalid response.'),
        mocker.call(''),
    ])


# Tests for TableUI public single character input methods.
def test_TableUI_all_yesnos(mocker, tableui_with_mocked_yesno):
    """The tested methods should call the
    :meth:`backjack.termui.TableUI._yesno_prompt`
    method with the prompt and default response.
    """
    ui, mock_yesno = tableui_with_mocked_yesno
    ui.doubledown_prompt()
    ui.hit_prompt()
    ui.nextgame_prompt()
    ui.split_prompt()
    catch_failure(mock_yesno.mock_calls[-5:], [
        mocker.call('Double down?', 'y'),
        mocker.call('Hit?', 'y'),
        mocker.call('Play another round?', 'y'),
        mocker.call('Split your hand?', 'y'),
    ])


# Tests for TableUI.update_count.
def test_TableUI__update_bet(mocker, tableui_with_mocked_main):
    """Given a count, :meth:`blackjack.termui.TableUI.update_count`
    should update the running count in the UI.
    """
    ui, mock_main = tableui_with_mocked_main
    ui.update_count('2')
    assert mock_main.mock_calls[-1:] == [
        mocker.call().send(('update_status', {'Count': '2',})),
    ]
