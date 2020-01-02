"""
players
~~~~~~~

The module contains the basic classes used by blackjack for handling 
players, including the dealer.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
class Player:
    """A blackjack player."""
    def __init__(self, hands: tuple = ()) -> None:
        """Initialize and instance of the class.
        
        :param hands: The player's hands of blackjack.
        :return: None.
        :rtype: None.
        """
        self.hands = hands