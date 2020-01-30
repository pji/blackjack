"""
willinsure
~~~~~~~~~~

The module contains the will_insure decision functions for players. 
These determine whether the player will insure the hand. They must:

* Accept self
* Accept a cards.Hand object
* Accept a game.Engine object
* Return a bool

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from blackjack.cards import Hand


# Functions.
def will_insure_always(self, the_game) -> bool:
    """The player will always buy the most insurance.
    
    :param hand: The hand to make the decision on.
    :param the_game: The information about the current game to use 
        to make a decision.
    :return: A decision whether to double down.
    :rtype: bool
    """
    return the_game.buyin / 2

def will_insure_never(self, the_game) -> bool:
    """The player will never buy insurance.
    
    :param hand: The hand to make the decision on.
    :param the_game: The information about the current game to use 
        to make a decision.
    :return: A decision whether to double down.
    :rtype: bool
    """
    return 0

def will_insure_user(self, the_game) -> bool:
    """Get a insurance decision from the user."""
#     is_yes = the_game.ui.input('insure')
    is_yes = the_game.ui.insure_prompt()
    insurance = 0
    if is_yes.value:
        insurance = the_game.buyin // 2
    return insurance

def will_insure_dealer(self, *args):
    """Dealers cannot insure."""
    msg = 'Dealers cannot insure.'
    raise TypeError(msg)


# List of valid will_insure functions.
# The following must be true to avoid unexpected behavior in randomly 
# generated players:
#   * The user version must be at index 0.
#   * The dealer version must be at index 1.
will_insures = [
    will_insure_user, 
    will_insure_dealer,
    will_insure_always, 
    will_insure_never
]
