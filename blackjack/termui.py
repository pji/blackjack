"""
termui
~~~~~~

This module manages a user interface run through a terminal.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from collections import namedtuple
import collections.abc as abc
from time import sleep
from typing import Any, Generator, Optional, Sequence

from blessed import Terminal
from blessed.keyboard import Keystroke


# Utility classes.
Field = namedtuple('Field', 'name fmt')


class Box:
    """A class to track the characters used to draw a box in a
    terminal.

    It has fifteen properties that return the character used for
    that part of the box:

    * top: The top
    * bot: The bottom
    * side: The sides
    * mhor: Interior horizontal lines
    * mver: Interior vertical lines
    * ltop: The top-left corner
    * mtop: Top mid-join
    * rtop: The top-right corner
    * lside: Left side mid-join
    * mid: Interior join
    * rside: Right side mid-join
    * lbot: Bottom-left corner
    * mbot: Bottom mid-join
    * rbot: Bottom-right corner
    """
    def __init__(self, kind: str = 'light', custom: str = None) -> None:
        self._names = [
            'top', 'bot', 'side',
            'mhor', 'mver',
            'ltop', 'mtop', 'rtop',
            'lside', 'mid', 'rside',
            'lbot', 'mbot', 'rbot',
        ]
        self._light = '──│─│┌┬┐├┼┤└┴┘'
        self._heavy = '━━┃━┃┏┳┓┣╋┫┗┻┛'
        self._light_double_dash = '╌╌╎╌╎' + self._light[3:]
        self._heavy_double_dash = '╍╍╏╍╏' + self._heavy[3:]
        self._light_triple_dash = '┄┄┆┄┆' + self._light[3:]
        self._heavy_triple_dash = '┅┅┇┅┇' + self._heavy[3:]
        self._light_quadruple_dash = '┈┈┊┈┊' + self._light[3:]
        self._heavy_quadruple_dash = '┉┉┋┉┋' + self._heavy[3:]
        if kind:
            self.kind = kind
        else:
            self.kind = 'light'
        if custom:
            self.custom = custom
            self.kind = 'custom'

    def __getattr__(self, name):
        try:
            index = self._names.index(name)
        except ValueError:
            return self.__dict__[name]
        return self._chars[index]

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        self._kind = value
        self._chars = getattr(self, f'_{value}')

    @property
    def custom(self):
        return self._custom

    @custom.setter
    def custom(self, value):
        strvalue = str(value)
        if len(strvalue) == 14:
            self._custom = str(strvalue)
            self._kind = 'custom'
        else:
            reason = 'The custom string must be 14 characters.'
            raise ValueError(reason)


# Terminal functions.
def splash(text: Sequence[str]) -> None:
    """Draw a splash screen in the terminal."""
    prompt = 'Press any key to continue.'
    term = Terminal()
    y = term.height // 2 - len(text) // 2
    with term.fullscreen(), term.cbreak():
        for line in text:
            x = term.width // 2 - len(line) // 2
            print(term.move(y, x) + line)
            y += 1
        print(
            term.move(
                term.height - 1,
                term.width // 2 - len(prompt) // 2
            )
            + prompt
        )
        term.inkey()


# TerminalController classes.
class TerminalController:
    data: Any = None
    fields: Any = None

    def __init__(self, term: Terminal = None) -> None:
        """Initialize an instance of the class.

        :param term: (Optional.) The blessed.Terminal object that
            runs the terminal output.
        :return: None.
        :rtype: NoneType
        """
        if not term:
            term = Terminal()
        self.term = term


class Page(TerminalController):
    """View pages of text in a terminal."""
    def __init__(
            self,
            text: str,
            title: str = '',
            frame: str = 'light',
            padding: int = 1,
            term: Optional[Terminal] = None
    ) -> None:
        self.frame = Box(kind=frame)
        self.padding = padding
        self.text = text
        self.title = title
        super().__init__(term)

    def draw(self) -> None:
        """Draw the page of text."""
        top = (
            self.frame.ltop
            + self.frame.top
            + self.title
            + self.frame.top * (self.term.width - len(self.title) - 3)
            + self.frame.rtop
        )
        space = str(self.term.width - 2 - 2)
        tmp = self.frame.mver + ' {:<' + space + '} ' + self.frame.mver
        blank = tmp.format('')
        bot = (
            self.frame.lbot
            + (self.frame.bot * (self.term.width - 2))
            + self.frame.rbot
        )

        lines = [top, ]
        for i in range(self.padding):
            lines.append(blank)
        for line in self.text.split('\n'):
            lines.append(tmp.format(line))
        for i in range(self.padding):
            lines.append(blank)
        filler = self.term.height - len(lines) - 1
        if filler:
            for i in range(filler):
                lines.append(blank)
        lines.append(bot)

        for y, line in enumerate(lines):
            print(self.term.move(y, 0) + line)


class Table(TerminalController):
    _header: tuple[str, ...]

    """Control a table displayed in the terminal."""
    def __init__(self,
                 title: str,
                 fields: abc.Sequence,
                 frame: Box = None,
                 data: abc.Sequence = None,
                 term: Terminal = None,
                 row_sep: bool = False,
                 rows: int = 1,
                 show_status: bool = False) -> None:
        """Initialize an instance of the class.

        :param title: The title for the table.
        :param fields: Information about the fields in the table. This
            is a sequence of sequences, one for each column in the
            table. The data in the child sequences matches the
            attributes of the FieldInfo class above.
        :param frame: (Optional.) A Box object that provides the
            characters used to frame the table.
        :param data: (Optional.) Initial values for the data table.
        :param term: (Optional.) The blessed.Terminal object that
            runs the terminal output.
        :param row_sep: (Optional.) Whether the frame elements that
            separate the rows are printed.
        :param rows: (Optional.) The number of rows in the data table.
        :return: None.
        :rtype: None.
        """
        self._data: list = []
        self._rows = 0
        self._table_bottom_rows = 1
        self._status_rows = 0

        self.title = title
        self.fields = [Field(*args) for args in fields]
        if not frame:
            frame = Box(custom='──   ───   ───')
        self.frame = frame
        self.rows = rows
        if data:
            self.data = list(data)
        self.row_sep = row_sep
        self.show_status = show_status
        if self.show_status:
            self._status_rows = 2
        self.status = {
            'Count': '0',
        }
        super().__init__(term)

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        self._fields = tuple(value)
        cls = self.__class__.__name__

        # Set _field_widths.
        w_name = f'__{cls}_field_widths'
        lengths = tuple(len(field.fmt.format(' ')) for field in self.fields)
        setattr(self, w_name, lengths)

        # Set _field_locs.
        fl_name = f'__{cls}_field_locs'
        locs = [1,]
        for width in self._field_widths[:-1]:
            locs.append(locs[-1] + width + 1)
        setattr(self, fl_name, tuple(locs))

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value):
        while value > len(self._data):
            self._data.append(['' for item in range(len(self.fields))])
        while value < len(self._data):
            self._data.pop()
        self._rows = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._rows = len(value)
        self._data = value

    @property
    def header(self) -> tuple[str, ...]:
        """Build the header lines for the UI."""
        try:
            return self._header

        except AttributeError:
            # Construct the table column labels.
            widths_fmt = ['{:<' + str(w) + '}' for w in self._field_widths]
            label_fmt = ' ' + ' '.join(widths_fmt)
            names = [field.name for field in self.fields]
            labels = label_fmt.format(*names)

            # Construct the header table.
            header = []
            header.append(self.term.bold + self.title)
            header.append('')
            header.append(labels)
            header.append(self._top)

            # Return the table of header lines.
            self._header = tuple(header)
            return self._header

    @property
    def _bot(self):
        """The bottom frame of the data table."""
        fields = [width * self.frame.bot for width in self._field_widths]
        middle = self.frame.mbot.join(fields)
        return self.frame.rbot + middle + self.frame.lbot

    @property
    def _field_locs(self):
        """The starting location for each cell in the table."""
        cls = self.__class__.__name__
        return getattr(self, f'__{cls}_field_locs')

    @property
    def _field_widths(self):
        """The widths of each cell in the table."""
        cls = self.__class__.__name__
        return getattr(self, f'__{cls}_field_widths')

    @property
    def _header_rows(self):
        return len(self.header)

    @property
    def _top(self):
        """The top frame of the data table."""
        fields = [width * self.frame.top for width in self._field_widths]
        middle = self.frame.mtop.join(fields)
        return self.frame.rtop + middle + self.frame.ltop

    @property
    def _y_error(self):
        """The row number for the error field."""
        return self._y_input + 1

    @property
    def _y_input(self):
        """The row number for the input field."""
        return (
            self._header_rows
            + len(self.data)
            + self._table_bottom_rows
            + self._status_rows
        )

    # Private methods.
    def _clear_footer(self) -> None:
        """Clear the bottom of the table and the footer."""
        bottom_table_row = self.rows + self._header_rows
        input_row = bottom_table_row + 1
        if not self.show_status:
            self._clear_row(input_row)
        self._clear_row(bottom_table_row)

    def _clear_row(self, y:int) -> None:
        """Clear a line in the UI."""
        print(self.term.move(y, 0) + ' ' * 80)

    def _clear_status(self) -> None:
        """Clear the status."""
        status_row = self._header_rows + self.rows + self._table_bottom_rows
        rows = [status_row + n for n in range(len(self.status) + 2)]
        for row in rows[::-1]:
            self._clear_row(row)

    def _draw_cell(self, row:int, col:int, value:Any) -> None:
        """Given a row, column, and value, draw that cell in the UI."""
        width = self._field_widths[col]
        if value:
            text = self.term.wrap(str(value), width)[0]
        else:
            text = ''
        y = row + 4
        x = list(self._field_locs)[col]
        fmt = self.fields[col].fmt
        print(self.term.move(y, x) + fmt.format(text))

    def _draw_header(self) -> None:
        """Draw the header lines."""
        for y, line in enumerate(self.header):
            print(self.term.move(y, 1) + line)

    def _draw_status(self):
        """Draw the status information."""
        y_start = len(self.data) + self._header_rows + self._table_bottom_rows
        for line, key in enumerate(self.status):
            y = y_start + line
            self._clear_row(y)
            text = f'{key}: {self.status[key]}'
            print(self.term.move(y, 1) + text)
        print(self.term.move(y + 1, 0) + self._bot)

    def _draw_table_bottom(self):
        """Draw the bottom of the table."""
        y = len(self.data) + self._header_rows
        print(self.term.move(y, 0) + self._bot)

    def _draw_table(self):
        """Draw a row in the table."""
        fields = self.frame.mver.join(field.fmt for field in self.fields)
        row_fmt = self.frame.rside + fields + self.frame.lside
        for index in range(len(self.data)):
            y = index + self._header_rows
            print(self.term.move(y, 0) + row_fmt.format(*self.data[index]))

    # Public methods.
    def clear(self):
        """Clear the UI."""
        footer_rows = 2
        rows = self._header_rows + self.rows + footer_rows
        for y in range(rows):
            self._clear_row(y)

    def draw(self):
        """Draw the entire UI."""
        self._draw_header()
        self._draw_table()
        self._draw_table_bottom()
        if self.show_status:
            self._draw_status()

    def error(self, msg: str) -> None:
        """Write an error to the UI."""
        y = self._y_error
        fmt = '{:<' + str(self.term.width) + '}'
        print(self.term.move(y, 1) + fmt.format(msg))

    def input(
            self,
            prompt: str,
            default: Optional[Keystroke] = None
    ) -> Optional[Keystroke]:
        """Prompt the user for input, and return the input.

        :param prompt: The input prompt.
        :param default: (Optional.) The value to return if the user
            doesn't provide input.
        :return: The user's input.
        :rtype: str
        """
        y = self._y_input
        fmt = '{:<' + str(self.term.width) + '}'
        print(self.term.move(y, 1) + fmt.format(prompt))
        with self.term.cbreak():
            resp: Optional[Keystroke] = self.term.inkey()
        print(self.term.move(y, 1) + fmt.format(''))
        if not resp or resp == '\n':
            resp = default
        return resp

    def input_multichar(
            self,
            prompt: str,
            default: str = ''
    ) -> str:
        """Prompt the user for input, and return the input.

        :param prompt: The input prompt.
        :param default: (Optional.) The value to return if the user
            doesn't provide input.
        :return: The user's input.
        :rtype: str
        """
        # Move to the input row and print the input prompt.
        y = (
            len(self.data)
            + self._header_rows
            + self._table_bottom_rows
            + self._status_rows
        )
        fmt = '{:<' + str(self.term.width) + '}'
        full_prompt = fmt.format(prompt + ' > ')
        print(self.term.move(y, 1) + full_prompt)
        x = len(prompt) + 2

        # Collect the input.
        text = ''
        with self.term.cbreak():
            resp: Optional[Keystroke] = self.term.inkey()
            while resp != '\n':
                char = str(resp)
                print(self.term.move(y, x) + char)
                x += 1
                text = text + char
                resp = self.term.inkey()

        # Rehome the cursor.
        print(self.term.move(y, 1) + fmt.format(''))

        # Return the input.
        if not text or text == '\n':
            return default
        return text

    def update(self, data:Sequence[list]) -> None:
        """Update the entire UI.

        :param data: A changed version of the data table.
        """
        while self.rows > len(data):
            if self.show_status:
                self._clear_status()
            self._clear_footer()
            self.rows -= 1
            self._draw_table_bottom()
            if self.show_status:
                self._draw_status()

        while self.rows < len(data):
            if self.show_status:
                self._clear_status()
            self._clear_footer()
            self.rows += 1
            self._draw_table_bottom()
            if self.show_status:
                self._draw_status()

        for row in range(len(self.data)):
            for col in range(len(self.data[row])):
                if self.data[row][col] != data[row][col]:
                    self._draw_cell(row, col, data[row][col])
        self.data = data

    def update_status(self, status: dict[str, str]) -> None:
        """Update the status fields."""
        self.status = status
        if self.show_status:
            self._draw_status()


# Main UI loop.
def main(
        ctlr: TerminalController = None,
        is_interactive=False,
        splash_text: Sequence[str] = ''
) -> Generator:
    """The main UI loop as a generator.

    Calling Parameters
    ------------------
    :param ctlr: (Optional.) A TerminalController object that will
        parse messages sent to the UI and update the terminal.

    Send Parameters
    ---------------
    TBD

    Yield
    -----
    :yield: None.
    :ytype: NoneType.

    Return
    ------
    :return: None.
    :rtype: NoneType
    """
    if not ctlr:
        ctlr = TerminalController()

    if splash_text:
        splash(splash_text)

    with ctlr.term.fullscreen(), ctlr.term.hidden_cursor():
        resp = None
        while True:
            event, *args = yield resp
            resp = getattr(ctlr, event)(*args)
            if is_interactive:
                sleep(.15)
