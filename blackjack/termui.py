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
Field = namedtuple('FieldInfo', 'name start fmt frame')


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
                 term: Terminal = None) -> None:
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
        :return: None.
        :rtype: None.
        """
        self.title = title
        self.fields = [Field(*args) for args in fields]
        if not frame:
            frame = Box(custom='──   ───   ───')
        self.frame = frame
        if not data:
            data = []
        self.data = list(data)
        super().__init__(term)


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
        yield None