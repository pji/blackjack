"""
termui
~~~~~~

This module manages a user interface run through a terminal.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from collections import namedtuple
import collections.abc as abc

from blessed import Terminal


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


# TerminalController classes.
class TerminalController:
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
        

class Table(TerminalController):
    """Control a table displayed in the terminal."""
    def __init__(self, title:str, fields: abc.Sequence, 
                 frame: Box = None, data: abc.Sequence = None,
                 term: Terminal = None, row_sep: bool = False) -> None:
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
        :param row_sep: Whether the frame elements that separate the 
            rows are printed.
        :return: None.
        :rtype: None.
        """
        self.title = title
        self.fields = [Field(*args) for args in fields]
        if not frame:
            frame = Box(custom='──   ───   ───')
        self.frame = frame
        if not data:
            data = [[field.fmt.format('') for field in self.fields],]
        self.data = list(data)
        self.row_sep = row_sep
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
    def _top(self):
        """The top frame of the data table."""
        fields = [width * self.frame.top for width in self._field_widths]
        middle = self.frame.mtop.join(fields)
        return self.frame.rtop + middle + self.frame.ltop
    
    def _draw_cell(self, row, col, value):
        """Given a row, column, and value, draw that cell in the UI."""
        width = self._field_widths[col]
        text = self.term.wrap(value, width)
        y = row + 4
        x = list(self._field_locs)[col]
        fmt = self.fields[col].fmt
        print(self.term.move(y, x) + fmt.format(text[0]))
    
    def _draw_table_bottom(self):
        """Draw the bottom of the table."""
        y = len(self.data) + 4
        print(self.term.move(y, 0) + self._bot)
    
    def _draw_table_headers(self):
        """Draw the column headers in the UI."""
        head_fmt = ' ' + ' '.join('{:<' + str(w) + '}' for w in self._field_widths)
        headers = [field.name for field in self.fields]
        print(self.term.move(2, 0) + head_fmt.format(*headers))
    
    def _draw_table(self) -> None:
        """Draw a row in the table."""
        fields = self.frame.mver.join(field.fmt for field in self.fields)
        row_fmt = self.frame.rside + fields + self.frame.lside
        for index in range(len(self.data)):
            y = index + 4
            print(self.term.move(y, 0) + row_fmt.format(*self.data[index]))
    
    def _draw_table_top(self):
        """Draw the top of the frame for the data table."""
        print(self.term.move(3, 0) + self._top)
    
    def _draw_title(self):
        """Draw the title in the UI."""
        print(self.term.move(0, 0) + self.term.bold + self.title)
    
    def draw(self):
        """Draw the entire UI."""
        self._draw_title()
        self._draw_table_headers()
        self._draw_table_top()
        self._draw_table()
        self._draw_table_bottom()
    
    def input(self, prompt, default=None):
        """Prompt the user for input, and return the input.
        
        :param prompt: The input prompt.
        :param default: (Optional.) The value to return if the user 
            doesn't provide input.
        :return: The user's input.
        :rtype: Any
        """
        y = len(self.data) + 5
        fmt = '{:<' + str(self.term.width) + '}'
        print(self.term.move(y, 1) + fmt.format(prompt))
        with self.term.cbreak():
            resp = self.term.inkey()
        print(self.term.move(y, 1) + fmt.format(''))
        if not resp:
            resp = default
        return resp
    
    def update(self, data):
        """Update the entire UI.
        
        :param data: A changed version of the data table.
        """
        for row in range(len(self.data)):
            for col in range(len(self.data[row])):
                if self.data[row][col] != data[row][col]:
                    self._draw_cell(row, col, data[row][col])
        self.data = data


# Main UI loop.
def main(ctlr: TerminalController = None) -> None:
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
    
    with ctlr.term.fullscreen(), ctlr.term.hidden_cursor():
        resp = None
        while True:
            event, *args = yield resp
            resp = getattr(ctlr, event)(*args)

