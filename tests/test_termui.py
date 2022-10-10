"""
test_termui.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.termui module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import unittest as ut
from unittest.mock import call, patch, PropertyMock

from blessed import Terminal
from blessed.keyboard import Keystroke

from blackjack import cards, game, model, players, termui


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


class SplashTestCase(ut.TestCase):
    topleft = '\x1b[1;2H'
    bold = '\x1b[1m'
    loc = '\x1b[{};{}H'

    def setUp(self):
        self.prompt = 'Press any key to continue.'
        self.text = ['spam', 'eggs',]
        self.term = Terminal()

    @patch('blessed.Terminal.inkey', return_value='\n')
    @patch('blackjack.termui.print')
    def test_draw(self, mock_print, mock_inkey):
        """When called with a sequence of strings, splash() should
        draw those strings in the middle of the terminal and wait
        until any key is pressed.
        """
        # Expected values.
        exp = [
            call(
                self.loc.format(
                    self.term.height // 2 - len(self.text) // 2 + 1,
                    self.term.width // 2 - len(self.text[0]) // 2 + 1
                )
                + self.text[0]
            ),
            call(
                self.loc.format(
                    self.term.height // 2 - len(self.text) // 2 + 2,
                    self.term.width // 2 - len(self.text[1]) // 2 + 1
                )
                + self.text[1]
            ),
            call(
                self.loc.format(
                    self.term.height,
                    self.term.width // 2 - len(self.prompt) // 2 + 1
                )
                + self.prompt
            ),
        ]

        # Run test and gather actuals.
        termui.splash(self.text)
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)


class TableTestCase(ut.TestCase):
    topleft = '\x1b[1;2H'
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

    def test_init_with_status(self):
        """When given show_status of True, the Table.show_status
        attribute should be true.
        """
        # Expected value.
        fields = (
            ('Eggs', '{}'),
            ('Baked Beans', '{}')
        )
        exp = {
            'title': 'Spam',
            'fields': tuple(termui.Field(*args) for args in fields),
            'show_status': True,
        }

        # Run test.
        obj = termui.Table(**exp)

        # Gather actuals.
        act = {attr: getattr(obj, attr) for attr in exp}

        # Determine test result.
        self.assertDictEqual(exp, act)

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
            call(self.loc.format(2, 2) + ''),
            call(self.loc.format(3, 2) + head),
            call(self.loc.format(4, 2) + frame),
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

        self.assertListEqual(expected, actual)

    @patch('blackjack.termui.print')
    def test_draw_with_status(self, mock_print):
        """If the Table.show_status attribute is True, the status
        information should be included in the draw.
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
        status = 'Count: 0'
        expected = [
            call(self.topleft + self.bold + title),
            call(self.loc.format(2, 2) + ''),
            call(self.loc.format(3, 2) + head),
            call(self.loc.format(4, 2) + frame),
            call(self.loc.format(5, 1) + row.format(*data[0])),
            call(self.loc.format(6, 1) + row.format(*data[1])),
            call(self.loc.format(7, 1) + frame),
            call(self.loc.format(8, 1) + ' ' * 80),
            call(self.loc.format(8, 2) + status),
            call(self.loc.format(9, 1) + frame),
        ]

        box = termui.Box(custom='──   ───   ───')
        ctlr = termui.Table(title, fields, data=data, show_status=True)
        main = termui.main(ctlr)
        next(main)
        main.send(('draw',))
        del main
        actual = mock_print.mock_calls

        self.assertListEqual(expected, actual)

    # Table.error() tests.
    @patch('blackjack.termui.print')
    def test_error(self, mock_print):
        """When called with a message, error() should write the error
        to the UI.
        """
        # Set up for expected value.
        msg = 'spam'
        fmt = '{:<80}'

        # Expected value.
        exp = [
            call(self.loc.format(8, 2) + fmt.format(msg)),
        ]

        # Test data and state.
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        ctlr = termui.Table('Eggs', fields)
        main = termui.main(ctlr)
        next(main)

        # Run test.
        act_resp = main.send(('error', msg))

        # Test tear down and gather actuals.
        del main
        act = mock_print.mock_calls[-1:]

        # Determine test result.
        self.assertEqual(exp, act)

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

    @patch('blessed.Terminal.inkey')
    @patch('blackjack.termui.print')
    def test_input_with_show_status(self, mock_print, mock_inkey):
        """When called with a prompt, input() should write the prompt
        to the UI and return the response from the user. When
        Table.show_status is True, the input line should be below the
        status line.
        """
        prompt = 'spam'
        fmt = '{:<80}'
        exp_print = [
            call(self.loc.format(9, 2) + fmt.format(prompt)),
            call(self.loc.format(9, 2) + fmt.format('')),
        ]
        exp_resp = 'n'

        mock_inkey.return_value = 'n'
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        ctlr = termui.Table('Eggs', fields, show_status=True)
        main = termui.main(ctlr)
        next(main)
        act_resp = main.send(('input', prompt))
        del main
        act_print = mock_print.mock_calls

        self.assertListEqual(exp_print, act_print)
        self.assertEqual(exp_resp, act_resp)

    # Table.input_multichar() tests.
    @patch('blessed.Terminal.inkey')
    @patch('blackjack.termui.print')
    def test_input_multichar(self, mock_print, mock_inkey):
        """When called with a prompt, input_multichar() should write the
        prompt to the UI and return the response from the user.
        """
        prompt = 'spam'
        fmt = '{:<80}'
        exp_print = [
            call(self.loc.format(7, 2) + fmt.format(prompt + ' > ')),
            call(self.loc.format(7, 7) + '2'),
            call(self.loc.format(7, 8) + '0'),
            call(self.loc.format(7, 2) + fmt.format('')),
        ]
        exp_resp = '20'

        mock_inkey.side_effect = ('2', '0', '\n')
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        ctlr = termui.Table('Eggs', fields)
        main = termui.main(ctlr)
        next(main)
        act_resp = main.send(('input_multichar', prompt))
        del main
        act_print = mock_print.mock_calls

        self.assertListEqual(exp_print, act_print)
        self.assertEqual(exp_resp, act_resp)

    @patch('blessed.Terminal.inkey')
    @patch('blackjack.termui.print')
    def test_input_multichar_default(self, mock_print, mock_inkey):
        """When called with a prompt and a default, input_number()
        should write the prompt to the UI and return the response
        from the user. If the user's response is only a newline,
        input_number() should return the default.
        """
        prompt = 'spam'
        fmt = '{:<80}'
        exp_print = [
            call(self.loc.format(7, 2) + fmt.format(prompt + ' > ')),
            call(self.loc.format(7, 2) + fmt.format('')),
        ]
        exp_resp = '20'

        mock_inkey.side_effect = ('\n', )
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        ctlr = termui.Table('Eggs', fields)
        main = termui.main(ctlr)
        next(main)
        act_resp = main.send(('input_multichar', prompt, exp_resp))
        del main
        act_print = mock_print.mock_calls

        self.assertListEqual(exp_print, act_print)
        self.assertEqual(exp_resp, act_resp)

    @patch('blessed.Terminal.inkey')
    @patch('blackjack.termui.print')
    @patch('blackjack.termui.clireader.view_text')
    def test_input_multichar_esc_to_help(
        self,
        mock_clir,
        mock_print,
        mock_inkey
    ):
        """When the user presses the escape key, input_multichar()
        should invoke the help screen.
        """
        prompt = 'spam'
        fmt = '{:<80}'
        with open('blackjack/data/rules.man') as fh:
            text = fh.read()
        title = 'rules.man'
        exp_clir = [
            call(text, title, 'man'),
        ]

        mock_inkey.side_effect = ('\x1b', 'x', '2', '0', '\n')
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        ctlr = termui.Table('Eggs', fields)
        main = termui.main(ctlr)
        next(main)
        act_resp = main.send(('input_multichar', prompt))
        act_clir = mock_clir.mock_calls
        del main

        self.assertListEqual(exp_clir, act_clir)

    @patch('blessed.Terminal.inkey')
    @patch('blackjack.termui.print')
    def test_input_multichar_with_status(self, mock_print, mock_inkey):
        """When called with a prompt, input_number() should write the
        prompt to the UI and return the response from the user.
        """
        # Set up expected.
        prompt = 'spam'
        fmt = '{:<80}'

        # Expected values.
        exp_print = [
            call(self.loc.format(9, 2) + fmt.format(prompt + ' > ')),
            call(self.loc.format(9, 7) + '2'),
            call(self.loc.format(9, 8) + '0'),
            call(self.loc.format(9, 2) + fmt.format('')),
        ]
        exp_resp = '20'

        # Test data and state.
        mock_inkey.side_effect = ('2', '0', '\n')
        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        ctlr = termui.Table('Eggs', fields, show_status=True)
        main = termui.main(ctlr)
        next(main)

        # Run test and gather actuals.
        act_resp = main.send(('input_multichar', prompt))
        del main
        act_print = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp_print, act_print)
        self.assertEqual(exp_resp, act_resp)

    # Table.status() tests.
    @patch('blackjack.termui.print')
    def test_status(self, mock_print):
        """When called with a status and its value, Table.status()
        should update the stored status value and then update the
        status field in the UI.
        """
        exp_status = {
            'Count': '9',
        }
        frame = '\u2500' * 23
        exp_calls = [
            call(self.loc.format(8, 1) + ' ' * 80),
            call(self.loc.format(8, 2) + f'Count: {exp_status["Count"]}'),
            call(self.loc.format(9, 1) + frame),
        ]

        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        data = [[0, 0], [0, 0]]
        ctlr = termui.Table('eggs', fields, data=data, show_status=True)
        main = termui.main(ctlr)
        next(main)

        main.send(('update_status', exp_status))

        main.close()
        act_status = ctlr.status
        act_calls = mock_print.mock_calls[-3:]

        self.assertDictEqual(exp_status, act_status)
        self.assertListEqual(exp_calls, act_calls)

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

    @patch('blackjack.termui.print')
    def test_update_smaller_table_with_status(self, mock_print):
        """When called with a data table that is smaller than the
        current table, update() should remove rows from the existing
        table to allow for the cell comparisons. It should then clear
        the removed rows from the UI and reprint the table bottom. If
        the status is displayed, it should be repositioned properly.
        """
        new_data = [[0, 0],]
        frame = '\u2500' * 23
        status = 'Count: 0'
        exp_calls = [
            call(self.loc.format(9, 1) + ' ' * 80),
            call(self.loc.format(8, 1) + ' ' * 80),
            call(self.loc.format(7, 1) + ' ' * 80),
            call(self.loc.format(6, 1) + frame),
            call(self.loc.format(7, 1) + ' ' * 80),
            call(self.loc.format(7, 2) + status),
            call(self.loc.format(8, 1) + frame),
        ]

        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        data = [[0, 0], [0, 0]]
        ctlr = termui.Table('eggs', fields, data=data, show_status=True)
        main = termui.main(ctlr)
        next(main)

        main.send(('update', new_data))

        main.close()
        act_calls = mock_print.mock_calls[-7:]

        self.assertListEqual(exp_calls, act_calls)

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

    @patch('blackjack.termui.print')
    def test_update_bigger_table_with_status(self, mock_print):
        """When called with a data table that is bigger than the
        current table, update() should add rows to the existing
        table to allow for the cell comparisons. It should then add
        the new rows to the UI and reprint the table bottom. It should
        then clear the removed rows from the UI and reprint the table
        bottom. If the status is displayed, it should be repositioned
        properly.
        """
        new_data = [[0, 0], [0, 0]]
        frame = '\u2500' * 23
        status = 'Count: 0'
        exp_calls = [
            call(self.loc.format(8, 1) + ' ' * 80),
            call(self.loc.format(7, 1) + ' ' * 80),
            call(self.loc.format(6, 1) + ' ' * 80),
            call(self.loc.format(7, 1) + frame),
            call(self.loc.format(8, 1) + ' ' * 80),
            call(self.loc.format(8, 2) + status),
            call(self.loc.format(9, 1) + frame),
            call(self.loc.format(6, 2) + ' ' * 10),
            call(self.loc.format(6, 13) + ' ' * 10),
        ]

        fields = [
            ('Name', '{:>10}'),
            ('Value', '{:>10}'),
        ]
        data = [[0, 0]]
        ctlr = termui.Table('eggs', fields, data=data, show_status=True)
        main = termui.main(ctlr)
        next(main)

        main.send(('update', new_data))

        act_calls = mock_print.mock_calls[-9:]
        main.close()

        self.assertListEqual(exp_calls, act_calls)


class TableUITestCase(ut.TestCase):
    def test_subclass(self):
        """TableUI is a subclass of game.EngineUI."""
        exp = game.EngineUI
        act = termui.TableUI
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
            'show_status': False,
        }

        ui = termui.TableUI(**exp)
        for attr in exp:
            act = getattr(ui, attr)

            self.assertEqual(exp[attr], act)

    def test_init_no_optional_attrs(self):
        """On initialization, TableUI should not require optional
        attributes.
        """
        exp = termui.Table

        ui = termui.TableUI()
        act = ui.ctlr

        self.assertTrue(isinstance(act, exp))

    def test__make_ctlr_with_show_status(self):
        """When TableUI.show_status is True, the Table returned
        should also have show_status set to True.
        """
        # Expected value.
        exp = True

        # Test data and state.
        ui = termui.TableUI(show_status=True)

        # Run test.
        ctlr = ui._make_ctlr()

        # Gather actual.
        act = ctlr.show_status

        # Determine test result.
        self.assertEqual(exp, act)

    @patch('blackjack.termui.main')
    def test_end(self, mock_main):
        """end() should terminate UI loop gracefully."""
        exp = call().close()

        ui = termui.TableUI()
        ui.start()
        ui.end()
        act = mock_main.mock_calls[-1]

        self.assertEqual(exp, act)

    @patch('blackjack.termui.main')
    def test_reset(self, mock_main):
        """When called, reset() should terminate the existing
        controller, create a new one, and prime it.
        """
        ui = termui.TableUI()
        ui.start()
        ui.reset()
        reset_ctlr = ui.ctlr
        exp = [
            call().close(),
            call(reset_ctlr, False, ''),
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
        ui = termui.TableUI()
        term = ui.ctlr
        exp = [
            call(ui.ctlr, False, ''),
            call().__next__(),
            call().send(('draw',))
        ]

        ui.start()
        act = mock_main.mock_calls

        self.assertListEqual(exp, act)

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
        ui = termui.TableUI()
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
        ui = termui.TableUI()
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
        ui = termui.TableUI()
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
    @patch('blackjack.termui.TableUI._update_bet')
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
        ui = termui.TableUI()
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
    @patch('blackjack.termui.TableUI._update_event')
    def test_event_updates(self, mock_update_event, _):
        """The tested methods should call the _update_event() method
        with the player and event text.
        """
        player = players.Player(name='spam', chips=100)
        exp = [
            call(player, 'Shuffles the deck.'),
        ]

        data = [[player, 80, 20, '', ''],]
        ui = termui.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.shuffles(player)
        act = mock_update_event.mock_calls[-1:]
        ui.end()

        self.assertEqual(exp, act)

    @patch('blackjack.termui.print')
    @patch('blackjack.termui.TableUI._update_hand')
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
        ui = termui.TableUI()
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
        ui = termui.TableUI()
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
