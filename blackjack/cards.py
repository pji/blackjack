"""
cards
~~~~~

The module contains the basic classes used by blackjack for handling 
cards.
"""
from blackjack.model import valfactory

# Validator functions.
def validate_rank(self, value: int) -> int:
    """Validate card ranks."""
    try:
        normal = int(value)
    except ValueError:
        reason = 'value must be able to be an int'
        raise TypeError(self.msg.format(reason))
    else:
        if normal < 1:
            reason = 'value must be greater than zero'
            raise ValueError(self.msg.format(reason))
        if normal > 13:
            reason = 'value must be less than 14'
            raise ValueError(self.msg.format(reason))
        return normal

def validate_suit(self, value):
    """Validate card suits."""
    suits = [
        'clubs',
        'diamonds',
        'hearts',
        'spades',
    ]
    
    try:
        normal = value.lower()
    except AttributeError:
        pass
    else:
        if normal in suits:
            return normal
    
    try:
        return suits[value]
    except IndexError:
        pass
    except TypeError:
        pass
    
    reason = 'not a valid suit'
    raise ValueError(self.msg.format(reason))
    

# Validator classes.
Rank = valfactory('Rank', validate_rank, 'Invalid rank ({}).')
Suit = valfactory('Suit', validate_suit, 'Invalid suit ({}).')


# Common classes.
class Card:
    """A playing card for the game of blackjack."""
    rank = Rank('rank')
    suit = Suit('suit')
    
    def __init__(self, rank: int = 11, suit: str = 'spades') -> None:
        """Initialize an instance of the class.
        
        :param rank: (Optional.) The rank (number value) of the card.
        :return: None.
        :rtype: None.
        """
        self.rank = rank
        self.suit = suit

