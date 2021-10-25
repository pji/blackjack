"""
test_termui.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.termui module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import unittest as ut
from unittest.mock import call, patch

from blessed import Terminal

from blackjack import termui


class BoxTestCase(ut.TestCase):
    def test_normal(self):
        "A Box object should return box characters."""
        expected = {
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
        for attr in expected:
            actual = getattr(box, attr)

            self.assertEqual(expected[attr], actual)

    def test_change_type(self):
        """If given a kind, the kind property should change the kind
        attribute and the _chars attribute.
        """
        expected = ['\u2500', '\u2501', '\u2508']

        box = termui.Box('light')
        actual = [box.top,]
        box.kind = 'heavy'
        actual.append(box.top)
        box.kind = 'light_quadruple_dash'
        actual.append(box.top)

        self.assertEqual(expected, actual)

    def test_custom(self):
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

        self.assertEqual(exp_kind, act_kind)
        self.assertEqual(exp_chars, act_chars)
        self.assertEqual(exp_sample, act_sample)

    def test_invalid_custom_string(self):
        """The passed custom string is not exactly fourteen characters
        long, a ValueError should be raised.
        """
        expected = ValueError

        with self.assertRaises(expected):
            box = termui.Box(custom='bad')


class TableTestCase(ut.TestCase):
    topleft = '\x1b[1;1H'
    bold = '\x1b[1m'
    loc = '\x1b[{};{}H'

    def test_init_attributes(self):
        """When initialized, Table should accept values for the
        class's required attributes.
        """
        fields = (
            ('Eggs', '{}'),
            ('Baked Beans', '{}')
        )
        expected = {
            'title': 'Spam',
            'fields': tuple(termui.Field(*args) for args in fields),
        }

        obj = termui.Table(**expected)
        for attr in expected:
            actual = getattr(obj, attr)

            self.assertEqual(expected[attr], actual)

    def test_init_no_data(self):
        """When initialized, if data is not passed, an initial empty
        table should be built.
        """
        expected = [['', ''],]

        fields = (
            ('Eggs', '{}'),
            ('Baked Beans', '{}')
        )
        attrs = {
            'title': 'Spam',
            'fields': [termui.Field(*args) for args in fields]
        }
        obj = termui.Table(**attrs)
        actual = obj.data

        self.assertEqual(expected, actual)

    def test_init_optional_attrs(self):
        """When initialized, Table should accept values for the
        class's optional attributes.
        """
        fields = (
            ('Eggs', '{}'),
            ('Baked Beands', '{}')
        )
        data = [
            [1, 2, 3],
            [4, 5, 6],
        ]
        expected = {
            'title': 'Spam',
            'fields': tuple(termui.Field(*args) for args in fields),
            'frame': termui.Box('light'),
            'data': data,
            'term': Terminal(),
            'row_sep': True,
            'rows': 2
        }

        obj = termui.Table(**expected)
        for attr in expected:
            actual = getattr(obj, attr)

            self.assertEqual(expected[attr], actual)

    def test_setting_rows_affects_data(self):
        """If the value of the rows attribute is changed, the size of
        the data table should change.
        """
        fields = (
            ('Eggs', '{}'),
            ('Baked Beans', '{}')
        )
        rows = 4
        exp = [
            ['', ''],
            ['', ''],
            ['', ''],
            ['', ''],
        ]

        table = termui.Table('spam', fields, rows=rows)
        act = table.data

        self.assertEqual(exp, act)

    def test_setting_data_affects_rows(self):
        """If the value of the data attribute is changes, the value
        of the rows attribute should be updated.
        """
        exp = 4

        fields = (
            ('Eggs', '{}'),
            ('Baked Beans', '{}')
        )
        data = [
            ['', ''],
            ['', ''],
            ['', ''],
            ['', ''],
        ]
        table = termui.Table('spam', fields, data=data)
        act = table.rows

        self.assertEqual(exp, act)

    # Table._draw_cell() tests.
    @patch('blackjack.termui.print')
    def test__draw_cell(self, mock_print):
        """When given the coordinates of a cell to draw, draw that
        cell in the UI.
        """
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        expected = [
            call(self.loc.format(5, 13) + fields[1][1].format('spam')),
        ]

        ctlr = termui.Table('Eggs', fields)
        main = termui.main(ctlr)
        next(main)
        main.send(('_draw_cell', 0, 1, 'spam'))
        del main
        actual = mock_print.mock_calls

        self.assertEqual(expected, actual)

    @patch('blackjack.termui.print')
    def test__draw_cell_wrap(self, mock_print):
        """When given the coordinates of a cell to draw, draw that
        cell in the UI.
        """
        text = '01234567890123456789'
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        expected = [
            call(self.loc.format(5, 13) + fields[1][1].format(text[10:])),
        ]

        ctlr = termui.Table('Eggs', fields)
        main = termui.main(ctlr)
        next(main)
        main.send(('_draw_cell', 0, 1, text))
        del main
        actual = mock_print.mock_calls

        self.assertEqual(expected, actual)

    @patch('blackjack.termui.print')
    def test__draw_cell_wrap_with_int(self, mock_print):
        """If a non-string is passed to _draw_cell, it should coerce
        the value to a string before trying to wrap it.
        """
        val = 12345678901234567890
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        expected = [
            call(self.loc.format(5, 13) + fields[1][1].format(str(val)[10:])),
        ]

        ctlr = termui.Table('Eggs', fields)
        main = termui.main(ctlr)
        next(main)
        main.send(('_draw_cell', 0, 1, val))
        del main
        actual = mock_print.mock_calls

        self.assertEqual(expected, actual)

    # Table.clear() tests.
    @patch('blackjack.termui.print')
    def test_clear(self, mock_print):
        """When called, clear should erase everything on the UI."""
        line = ' ' * 80
        exp = [call(self.loc.format(y, 1) + line)
               for y in range(1, 9)]

        title = 'Spam'
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        data = [[1, 2], [3, 4]]
        box = termui.Box(custom='──   ───   ───')
        ctlr = termui.Table(title, fields, data=data)
        main = termui.main(ctlr)
        next(main)
        main.send(('clear',))
        del main
        act = mock_print.mock_calls[-8:]

        self.assertEqual(exp, act)

    # Table.draw() tests.
    @patch('blackjack.termui.print')
    def test_draw(self, mock_print):
        """When called, draw should draw the entire UI to the
        terminal.
        """
        title = 'Spam'
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        head = ' ' + ' '.join('{:<10}'.format(f[0]) for f in fields)
        data = [[1, 2], [3, 4]]
        row = ' ' + ' '.join(field[1] for field in fields) + ' '
        frame = '\u2500' * 23
        expected = [
            call(self.topleft + self.bold + title),
            call(self.loc.format(3, 1) + head),
            call(self.loc.format(4, 1) + frame),
            call(self.loc.format(5, 1) + row.format(*data[0])),
            call(self.loc.format(6, 1) + row.format(*data[1])),
            call(self.loc.format(7, 1) + frame),
        ]

        box = termui.Box(custom='──   ───   ───')
        ctlr = termui.Table(title, fields, data=data)
        main = termui.main(ctlr)
        next(main)
        main.send(('draw',))
        del main
        actual = mock_print.mock_calls

        self.assertEqual(expected, actual)

    # Table.input() tests.
    @patch('blessed.Terminal.inkey')
    @patch('blackjack.termui.print')
    def test_input(self, mock_print, mock_inkey):
        """When called with a prompt, input() should write the prompt
        to the UI and return the response from the user.
        """
        prompt = 'spam'
        fmt = '{:<80}'
        exp_print = [
            call(self.loc.format(7, 2) + fmt.format(prompt)),
            call(self.loc.format(7, 2) + fmt.format('')),
        ]
        exp_resp = 'n'

        mock_inkey.return_value = 'n'
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        ctlr = termui.Table('Eggs', fields)
        main = termui.main(ctlr)
        next(main)
        act_resp = main.send(('input', prompt))
        del main
        act_print = mock_print.mock_calls

        self.assertEqual(exp_print, act_print)
        self.assertEqual(exp_resp, act_resp)

    @patch('blessed.Terminal.inkey')
    @patch('blackjack.termui.print')
    def test_input_default(self, mock_print, mock_inkey):
        """If the user input is empty, return the default value
        instead.
        """
        prompt = 'spam'
        fmt = '{:<80}'
        exp_print = [
            call(self.loc.format(7, 2) + fmt.format(prompt)),
            call(self.loc.format(7, 2) + fmt.format('')),
        ]
        exp_resp = 'n'

        mock_inkey.return_value = ''
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        ctlr = termui.Table('Eggs', fields)
        main = termui.main(ctlr)
        next(main)
        act_resp = main.send(('input', prompt, exp_resp))
        del main
        act_print = mock_print.mock_calls

        self.assertEqual(exp_print, act_print)
        self.assertEqual(exp_resp, act_resp)

    # Table.update() tests.
    @patch('blackjack.termui.Table._draw_cell')
    def test_update(self, mock_draw_cell):
        """When called with a data table, update() should compare the
        new table with the existing one, write any new values to the
        UI, and then replace the old table with the new one.
        """
        exp_data = [[0, 0], [0, 'spam']]
        exp_calls = [
            call(1, 1, 'spam'),
        ]

        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        data = [[0, 0], [0, 0]]
        ctlr = termui.Table('eggs', fields, data=data)
        main = termui.main(ctlr)
        next(main)
        main.send(('update', exp_data))
        del main
        act_data = ctlr.data
        act_calls = mock_draw_cell.mock_calls

        self.assertEqual(exp_data, act_data)
        self.assertEqual(exp_calls, act_calls)

    # Table.update() tests.
    @patch('blackjack.termui.print')
    def test_update_smaller_table(self, mock_print):
        """When called with a data table that is smaller than the
        current table, update() should remove rows from the existing
        table to allow for the cell comparisons. It should then clear
        the removed rows from the UI and reprint the table bottom.
        """
        new_data = [[0, 0],]
        frame = '\u2500' * 23
        exp_calls = [
            call(self.loc.format(8, 1) + ' ' * 80),
            call(self.loc.format(7, 1) + ' ' * 80),
            call(self.loc.format(6, 1) + frame),
        ]

        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        data = [[0, 0], [0, 0]]
        ctlr = termui.Table('eggs', fields, data=data)
        main = termui.main(ctlr)
        next(main)
        main.send(('update', new_data))
        main.close()
        act_calls = mock_print.mock_calls[-4:]

        self.assertListEqual(exp_calls, act_calls)

    # Table.update() tests.
    @patch('blackjack.termui.print')
    def test_update_bigger_table(self, mock_print):
        """When called with a data table that is bigger than the
        current table, update() should add rows to the existing
        table to allow for the cell comparisons. It should then add
        the new rows to the UI and reprint the table bottom.
        """
        new_data = [[0, 0], [0, 0]]
        frame = '\u2500' * 23
        exp_calls = [
            call(self.loc.format(7, 1) + ' ' * 80),
            call(self.loc.format(6, 1) + ' ' * 80),
            call(self.loc.format(7, 1) + frame),
        ]

        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        data = [[0, 0]]
        ctlr = termui.Table('eggs', fields, data=data)
        main = termui.main(ctlr)
        next(main)
        main.send(('update', new_data))
        main.close()
        act_calls = mock_print.mock_calls[:-2]

        self.assertListEqual(exp_calls, act_calls)


class mainTestCase(ut.TestCase):
    def test_init_with_params(self):
        """main() should create its own instances of term and ctlr if
        none are supplied.
        """
        ctlr = termui.TerminalController()
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
