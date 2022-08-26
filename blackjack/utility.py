"""
utility
~~~~~~~

Miscellaneous objects for the blackjack module.
"""
splash_title = (
    '╔╗  ║   ╔═╗ ╔═╗ ║ ║',
    '║║  ║   ║ ║ ║   ╠═╝',
    '╠╩╗ ║   ╠═╣ ║   ╠═╗',
    '║ ║ ║   ║ ║ ║   ║ ║',
    '╚═╝ ╚══ ║ ║ ╚═╝ ║ ║',
    '',
    '    ║ ╔═╗ ╔═╗ ║ ║  ',
    '    ║ ║ ║ ║   ╠═╝  ',
    '    ║ ╠═╣ ║   ╠═╗  ',
    '    ║ ║ ║ ║   ║ ║  ',
    '  ╚═╝ ║ ║ ╚═╝ ║ ║  ',
)


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
