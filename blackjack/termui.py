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
import clireader

from blackjack import model, players
from blackjack.utility import Box


# Utility classes.
Field = namedtuple('Field', 'name fmt')


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
class Table(model.TerminalController):
    _header: tuple[str, ...]

    """Control a table displayed in the terminal."""
    def __init__(
        self,
        title: str,
        fields: abc.Sequence,
        frame: Box = None,
        data: abc.Sequence = None,
        term: Terminal = None,
        row_sep: bool = False,
        rows: int = 1,
        show_status: bool = False
    ) -> None:
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

    def _show_help(self):
        clireader.main('blackjack/data/rules.man', 'man')

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
                if resp == '\x1b':
                    self._show_help()
                    self.clear()
                    self.draw()
                    print(self.term.move(y, 1) + full_prompt)
                else:
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


class TableUI(model.EngineUI):
    """A table-based terminal UI for blackjack."""
    loop: Generator

    # General operation methods.
    def __init__(self, ctlr: Optional[model.TerminalController] = None,
                 seats: int = 1,
                 show_status: bool = False) -> None:
        """Initialize and instance of the class.

        :param ctlr: (Optional.) The TerminalController object running
            the UI.
        :param seats: (Optional.) The number of seats that will be
            available for the game.
        """
        self.seats = seats
        self.show_status = show_status
        if not ctlr:
            ctlr = self._make_ctlr()
        self.ctlr = ctlr
        self.is_interactive = False

    def _make_ctlr(self):
        """Returns a Table object for blackjack."""
        fields = (
            ('Player', '{:<14}'),
            ('Chips', '{:>7}'),
            ('Bet', '{:>3}'),
            ('Hand', '{:<27}'),
            ('Event', '{:<23}'),
        )
        return Table(
            'Blackjack',
            fields,
            rows=self.seats,
            show_status=self.show_status
        )

    def end(self):
        """End the UI loop gracefully."""
        self.loop.close()

    def reset(self):
        """Reset the UI."""
        self.end()
        self.ctlr = self._make_ctlr()
        self.start(self.is_interactive)

    def start(self, is_interactive=False, splash_title=''):
        """Start the UI."""
        self.is_interactive = is_interactive
        self.loop = main(self.ctlr, is_interactive, splash_title)
        next(self.loop)
        self.loop.send(('draw',))

    # Input methods.
    def _prompt(self, prompt, default):
        """Prompt for a response from the user."""
        return self.loop.send(('input', prompt, default))

    def _yesno_prompt(self, prompt, default):
        prompt = f'{prompt} [yn] > '
        error = False
        valid = None
        while not valid:
            resp = self._prompt(prompt, default)
            try:
                valid = model.IsYes(resp)
            except (AttributeError, ValueError):
                self.loop.send(('error', 'Invalid response.'))
                error = True
        if error:
            self.loop.send(('error', ''))
        return valid

    def bet_prompt(self, bet_min: int, bet_max: int) -> model.Bet:
        """Ask user for a bet.."""
        prompt = f'How much do you wish to bet? [{bet_min}-{bet_max}]'
        default = str(bet_min)
        error = False
        valid = None
        while not valid:
            resp = self.loop.send(('input_multichar', prompt, default))
            try:
                valid = model.Bet(resp, bet_max, bet_min)
            except ValueError:
                self.loop.send(('error', 'Invalid response.'))
                error = True
        if error:
            self.loop.send(('error', ''))
        return valid

    def doubledown_prompt(self) -> model.IsYes:
        """Ask user if they want to double down."""
        prompt = 'Double down?'
        default = 'y'
        return self._yesno_prompt(prompt, default)

    def hit_prompt(self) -> model.IsYes:
        """Ask user if they want to hit."""
        prompt = 'Hit?'
        default = 'y'
        return self._yesno_prompt(prompt, default)

    def insure_prompt(self, insure_max: int) -> model.Bet:
        """Ask user if they want to insure."""
        prompt = f'How much insurance do you want? [0-{insure_max}]'
        default = '0'
        error = False
        valid = None
        while not valid:
            resp = self.loop.send(('input_multichar', prompt, default))
            try:
                valid = model.Bet(resp, insure_max, 0)
            except ValueError:
                self.loop.send(('error', 'Invalid response.'))
                error = True
        if error:
            self.loop.send(('error', ''))
        return valid

    def nextgame_prompt(self) -> model.IsYes:
        """Ask user if they want to play another round."""
        prompt = 'Play another round?'
        default = 'y'
        return self._yesno_prompt(prompt, default)

    def split_prompt(self) -> model.IsYes:
        """Ask user if they want to split."""
        prompt = 'Split your hand?'
        default = 'y'
        return self._yesno_prompt(prompt, default)

    # Update methods.
    def _get_field_index(self, needed: Sequence[str]) -> list:
        """Get the indices the given fields of the data table.

        :param needed: The names of the fields you need the indexes
            for.
        :return: A list of the indices.
        :rtype: list
        """
        if self.ctlr is None:
            msg = 'Controller undefined.'
            raise RuntimeError(msg)
        fields = [field.name for field in self.ctlr.fields]
        return [fields.index(field) for field in needed]

    def _get_player_row_and_data(self, player: players.Player) -> tuple:
        """Get the data table row for the given player.

        :param player: The player to get the row for.
        :return: An index and a copy of the data table.
        :rtype: tuple
        """
        # Get the player's row to update.
        # Since Table determines which fields to updata by
        # looking for changes in the data table, it's very important
        # that we create a copy of data here.
        if self.ctlr is None:
            msg = 'Control uninitialized.'
            raise RuntimeError(msg)
        data = [row[:] for row in self.ctlr.data]
        playerlist = [row[0] for row in data]
        row = playerlist.index(player)
        return row, data

    def _update_bet(self, player, bet, event, split=False):
        """The player's bet and chips information needs to be
        updated.

        :param player: The player whose row to update.
        :param bet: The player's bet.
        :param event: The event that occurred.
        :param split: Whether the update is for the split hand.
        :return: None.
        :rtype: NoneType
        """
        row, data = self._get_player_row_and_data(player)
        if split and len(player.hands) == 2:
            row += 1

        affected_fields = ('Chips', 'Bet', 'Event')
        i_chips, i_bet, i_event = self._get_field_index(affected_fields)

        if not split:
            data[row][i_chips] = player.chips
        data[row][i_bet] = bet
        data[row][i_event] = event
        self.loop.send(('update', data))

    def _update_event(self, player, event):
        """The player's event information needs to be updated.
        """
        row, data = self._get_player_row_and_data(player)

        affected_fields = ('Event',)
        i_event, = self._get_field_index(affected_fields)

        data[row][i_event] = event
        self.loop.send(('update', data))

    def _update_hand(self, player, hand, event):
        """The player's hand information needs to be updated."""
        row, data = self._get_player_row_and_data(player)
        if len(player.hands) == 2:
            if player.hands.index(hand) == 1:
                row += 1

        affected_fields = ('Hand', 'Event')
        i_hand, i_event = self._get_field_index(affected_fields)

        data[row][i_hand] = str(hand)
        data[row][i_event] = event
        self.loop.send(('update', data))

    def bet(self, player, bet):
        """Player places initial bet."""
        self._update_bet(player, bet, 'Bets.')

    def cleanup(self):
        """Clean up information from the previous round."""
        data = [row[:] for row in self.ctlr.data]
        affected = ['Player', 'Chips', 'Bet', 'Hand', 'Event']
        i_play, i_chp, i_bet, i_hand, i_event = self._get_field_index(affected)
        data = [row for row in data if isinstance(row[i_play], players.Player)]
        for row in data:
            row[i_chp] = row[i_play].chips
            row[i_bet] = ''
            row[i_hand] = ''
            row[i_event] = ''
        self.loop.send(('update', data))

    def deal(self, player, hand):
        """Player recieves initial hand."""
        self._update_hand(player, hand, 'Takes hand.')

    def doubledown(self, player, bet):
        """Player doubles down."""
        self._update_bet(player, bet, 'Doubles down.')

    def flip(self, player, hand):
        """Player flips a card."""
        self._update_hand(player, hand, 'Flips card.')

    def hit(self, player, hand):
        """Player hits."""
        self._update_hand(player, hand, 'Hits.')

    def insures(self, player, bet):
        """Player insures their hand."""
        self._update_bet(player, bet, f'Buys {bet} insurance.')

    def insurepay(self, player, bet):
        """Insurance is paid to player."""
        self._update_bet(player, bet, f'Insurance pays {bet}.')

    def joins(self, player):
        """Player joins the game.

        :param player: The player to add to the game.
        :return: None.
        :rtype: NoneType.
        """
        row, data = self._get_player_row_and_data('')
        affected = ['Player', 'Chips', 'Event']
        i_play, i_chip, i_event = self._get_field_index(affected)

        data[row][i_play] = player
        data[row][i_chip] = player.chips
        data[row][i_event] = 'Sits down.'

        self.loop.send(('update', data))

    def leaves(self, player):
        """Player leaves the game.

        :param player: The player to remove from the game.
        :return: None.
        :rtype: NoneType.
        """
        row, data = self._get_player_row_and_data(player)
        cats = ['Player', 'Chips', 'Bet', 'Hand', 'Event']
        i_play, i_chip, i_bet, i_hand, i_event = self._get_field_index(cats)

        # Send leaving message to UI.
        data[row][i_chip] = ''
        data[row][i_bet] = ''
        data[row][i_hand] = ''
        data[row][i_event] = 'Walks away.'
        self.loop.send(('update', data))

        # Remove the player from the data table.
        self.ctlr.data[row][i_play] = ''

    def loses(self, player):
        """Player loses."""
        self._update_bet(player, '', 'Loses.')

    def loses_split(self, player):
        """Player loses on their split hand."""
        self._update_bet(player, '', 'Loses.', True)

    def shuffles(self, player):
        """The deck is shuffled."""
        self._update_event(player, 'Shuffles the deck.')

    def splits(self, player, bet):
        """Player splits their hand."""
        row, data = self._get_player_row_and_data(player)
        cats = ['Player', 'Chips', 'Bet', 'Hand', 'Event']
        i_play, i_chip, i_bet, i_hand, i_event = self._get_field_index(cats)

        # Update existing row.
        data[row][i_chip] = player.chips
        data[row][i_bet] = bet
        data[row][i_hand] = str(player.hands[0])
        data[row][i_event] = 'Splits hand.'

        # Build the new split row and add it.
        new_row = ['' for field in range(len(self.ctlr.fields))]
        new_row[i_play] = '  \u2514\u2500'
        new_row[i_bet] = bet
        new_row[i_hand] = str(player.hands[1])
        data.insert(row + 1, new_row)

        self.loop.send(('update', data))

    def stand(self, player, hand):
        """Player stands."""
        self._update_hand(player, hand, 'Stands.')

    def tie(self, player, bet):
        """Player ties."""
        self._update_bet(player, '', f'Ties {bet}.')

    def ties_split(self, player, bet):
        """Player ties."""
        self._update_bet(player, '', f'Ties {bet}.', True)

    def update_count(self, count):
        """Update the running card count in the UI."""
        status = {
            'Count': f'{count}'
        }
        self.loop.send(('update_status', status))

    def wins(self, player, bet):
        """Player wins."""
        self._update_bet(player, '', f'Wins {bet}.')

    def wins_split(self, player, bet):
        """Player wins on their split hand."""
        self._update_bet(player, '', f'Wins {bet}.', True)


# Main UI loop.
def main(
        ctlr: model.TerminalController = None,
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
        ctlr = model.TerminalController()

    if splash_text:
        splash(splash_text)

    with ctlr.term.fullscreen(), ctlr.term.hidden_cursor():
        resp = None
        while True:
            event, *args = yield resp
            resp = getattr(ctlr, event)(*args)
            if is_interactive:
                sleep(.15)
