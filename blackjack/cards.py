"""
cards
~~~~~

The module contains the basic classes used by blackjack for handling 
cards.
"""
from collections import OrderedDict
from itertools import product

from blackjack.model import Boolean, valfactory

# Global values.
UP = True
DOWN = False
RANKS = list(range(1, 14))
SUITS = OrderedDict([
    ('clubs', '♣'),
    ('diamonds', '♦'),
    ('hearts', '♥'),
    ('spades', '♠'),
])


# Validator functions.
def validate_rank(self, value: int) -> int:
    """Validate card ranks."""
    try:
        normal = int(value)
    except ValueError:
        reason = 'value must be able to be an int'
        raise TypeError(self.msg.format(reason))
    else:
        if normal < RANKS[0]:
            reason = 'value must be greater than zero'
            raise ValueError(self.msg.format(reason))
        if normal > RANKS[-1]:
            reason = 'value must be less than 14'
            raise ValueError(self.msg.format(reason))
        return normal

def validate_suit(self, value):
    """Validate card suits."""
    try:
        normal = value.lower()
    except AttributeError:
        pass
    else:
        if normal in SUITS:
            return normal
    
    try:
        return list(SUITS.keys())[value]
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
    facing = Boolean('facing')
    
    def __init__(self, rank: int = 11, suit: str = 'spades',
                 facing: bool = UP) -> None:
        """Initialize an instance of the class.
        
        :param rank: (Optional.) The rank (number value) of the card.
        :param suit: (Optional.) The suit of the card.
        :param facing: (Optional.) Whether the card is face up. True 
            is face up. False is face down.
        :return: None.
        :rtype: None.
        """
        self.rank = rank
        self.suit = suit
        self.facing = facing
    
    def __repr__(self):
        cls = self.__class__
        tmp = '{}(rank={}, suit={!r}, facing={})'
        return tmp.format(cls.__name__, self.rank, self.suit, self.facing)
    
    def __str__(self):
        rank_translate = {
            1: 'A',
            11: 'J',
            12: 'Q',
            13: 'K',
        }
        rank = self.rank
        if rank in rank_translate:
            rank = rank_translate[rank]
        suit = SUITS[self.suit]
        return f'{rank}{suit}'
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return (self.suit == other.suit and self.rank == other.rank)
        return NotImplemented
    
    def __ne__(self, other):
        result = self.__eq__(other)
        if isinstance(result, bool):
            return not result
        return result


class Deck:
    """A deck of playing cards for blackjack."""
    def __init__(self, cards: list = None) -> None:
        """Initialize and instance of the class.
        
        :param cards: (Optional.) A list containing the cards held by 
            the deck.
        :return: None
        :rtype: None
        """
        self.cards = cards
        if not self.cards:
            self.cards = []
    
    def __eq__(self, other):
        if isinstance(other, Deck):
            return self.cards == other.cards
        return NotImplemented
    
    # Sized protocol.
    def __len__(self):
        """Get the number of cards in the deck."""
        return len(self.cards)
    
    # Iterator protocol.
    
    
    # Iterable protocol.
    # Container protocol.
    # Collection protocol.
    # Reversible protocol.
    # Sequence protocol.
    # MutableSequence protocol.
    
    @classmethod
    def build(cls, num_decks: int = 1):
        """(Class method.) Create a Deck object that is populated 
        with cards.
        
        :param num_decks: (Optional.) The number of standard decks to 
            use when constructing the deck.
        :return: An instance of Deck that contains Card objects.
        :rtype: Deck
        """
        d = cls()
        std_deck = [Card(rank, suit) for rank, suit in product(RANKS, SUITS)]
        for i in range(num_decks):
            d.cards.extend(std_deck)
        return d