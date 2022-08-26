"""
pageui
~~~~~~

A CLI paging interface for the display of text.
"""
from textwrap import wrap
from time import sleep
from typing import Generator, Optional

from blessed import Terminal

from blackjack.model import TerminalController
from blackjack.utility import Box


class Page(TerminalController):
    """View pages of text in a terminal."""
    def __init__(
            self,
            text: str = '',
            title: str = '',
            frame: str = 'light',
            padding: int = 1,
            term: Optional[Terminal] = None
    ) -> None:
        self.frame = Box(kind=frame)
        self.padding = padding
        self.text = text
        self.title = title
        self.current_page = 0
        super().__init__(term)

    @property
    def pages(self) -> list[list[str]]:
        if '_pages' not in self.__dict__:
            width = self.term.width + 1 - 2 - self.padding * 2
            lines_per_page = self.term.height + 1 - 2 - self.padding * 2
            wrapped = wrap(self.text, width)
            self._pages = []
            for i in range(0, len(wrapped), lines_per_page):
                self._pages.append(wrapped[i: i + lines_per_page])
        return self._pages

    def _draw_command_hints(self) -> None:
        hints = []
        if len(self.pages) > 1:
            hints.append(self.term.reverse + '>' + self.term.reverse + 'Next')
        if len(self.pages) > 1 and self.current_page != 0:
            hints.append(self.term.reverse + '<' + self.term.reverse + 'Back')
        for i, hint in enumerate(hints):
            y = self.term.height
            x = self.term.width - 5 - 3 - 6 * i
            print(self.term.move(y, x) + hint)

    def _draw_frame(self) -> None:
        """Draw the frame around the page."""
        top = (
            self.frame.ltop
            + self.frame.top
            + self.title
            + self.frame.top * (self.term.width - len(self.title) - 3)
            + self.frame.rtop
        )
        mid = (
            self.frame.mver
            + (' ' * (self.term.width - 2))
            + self.frame.mver
        )
        bot = (
            self.frame.lbot
            + (self.frame.bot * (self.term.width - 2))
            + self.frame.rbot
        )

        print(self.term.move(0, 0) + top)
        for y in range(1, self.term.height):
            print(self.term.move(y, 0) + mid)
        print(self.term.move(self.term.height, 0) + bot)

    def back(self) -> None:
        """Go back to the previous page of text."""
        self.current_page -= 1
        self.draw()

    def draw(self) -> None:
        """Draw the page of text."""
        # Draw the frame.
        self._draw_frame()
        self._draw_command_hints()

        # Draw the text.
        text = self.pages[self.current_page]
        y = self.padding + 1
        x = self.padding + 1
        for line in text:
            print(self.term.move(y, x) + line)
            y += 1

    def load(self, text: str, title: str = '') -> None:
        """Update the text pages being shown."""
        self.text = text
        self.title = title
        self.current_page = 0
        if '_pages' in self.__dict__:
            del self._pages
        self.draw()

    def next(self) -> None:
        """Advance to the next page of text."""
        self.current_page += 1
        self.draw()


class PageUI:
    def __init__(self, ctlr: Optional[Page] = None) -> None:
        if not ctlr:
            ctlr = Page()
        self.ctlr = ctlr


# Main UI loop.
def main(
        ctlr: TerminalController = None,
        is_interactive=False
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

    with ctlr.term.fullscreen(), ctlr.term.hidden_cursor():
        resp = None
        while True:
            event, *args = yield resp
            resp = getattr(ctlr, event)(*args)
            if is_interactive:
                sleep(.15)
