"""
cards
~~~~~

The module contains the basic classes used by blackjack for handling 
cards.
"""
from collections import OrderedDict
from collections.abc import MutableSequence
from copy import copy
from itertools import product
from random import randrange, shuffle

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
        if self.facing == DOWN:
            return '\u2500\u2500'
        
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
    
    def flip(self):
        """Flip the facing of the card."""
        self.facing = not self.facing


class Pile(MutableSequence):
    """A generic pile of cards."""
    def __init__(self, cards: list = None) -> None:
        """Initialize and instance of the class.
        
        :param cards: (Optional.) A list containing the cards held by 
            the deck.
        :return: None
        :rtype: None
        """
        self._iter_index = 0
        self.cards = cards
        if not self.cards:
            self.cards = []
    
    def __eq__(self, other):
        if isinstance(other, Pile):
            return self.cards == other.cards
        return NotImplemented
    
    # Sized protocol.
    def __len__(self):
        return len(self.cards)
    
    # Iterator protocol.
    def __iter__(self):
        return self.copy()
    
    def __next__(self):
        if self._iter_index >= len(self):
            raise StopIteration
        card = self.cards[self._iter_index]
        self._iter_index += 1
        return card
    
    # Container protocol.
    def __contains__(self, item):
        return item in self.cards
    
    # Reversible protocol.
    def __reversed__(self):
        cls = self.__class__
        return cls(self.cards[::-1])
    
    # Sequence protocol.
    def __getitem__(self, key):
        return self.cards.__getitem__(key)
    
    # MutableSequence protocol.
    def __setitem__(self, key, value):
        self.cards.__setitem__(key, value)
    
    def __delitem__(self, key):
        self.cards.__delitem__(key)
    
    def insert(self, key, item):
        self.cards.insert(key, item)
    
    #Utility methods.
    def copy(self):
        """Return a copy of the Deck object."""
        return copy(self)


class Deck(Pile):
    """A deck of playing cards for blackjack."""
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
        ranks = reversed(RANKS)
        std_deck = [Card(rank, suit, DOWN) for suit, rank 
                    in product(SUITS, ranks)]
        for i in range(num_decks):
            d.cards.extend(std_deck)
        return d
    
    def draw(self):
        """Draw the top card from the deck.
        
        NOTE: Due to how lists work, it is more efficient for the top 
        of the deck to be index -1 rather than index 0, even though 
        this is counterintuitive.
        
        :return: The top card from the deck.
        :rtype: Card
        """
        return self.pop()
    
    def shuffle(self):
        """Randomize the order of the deck."""
        shuffle(self.cards)
    
    def random_cut(self):
        """Remove the last 60-75 cards from the deck. This is done 
        before a round of blackjack begins to make it harder to 
        count cards.
        """
        num = randrange(60, 76)
        self.cards = self.cards[num:]


class Hand(Pile):
    """A hand of blackjack.
    
    NOTE: Five card charlie (winning if you get five cards without 
    busting) is a house rule. This implementation is based on the 
    Bicycle rules for Blackjack at bicyclecards.com, so it doesn't 
    implement that rule.
    """
    def append(self, item):
        self.cards.append(item)
    
    def score(self):
        scores = set()
        
        # Sorting by ranks makes it easier to score.
        ranks = sorted([card.rank for card in self.cards])
        
        # Splitting out the aces because they are complicated.
        aces = [rank for rank in ranks if rank == 1]
        other = [rank for rank in ranks if rank > 1]
        
        # Doing the easy scoring first.
        score = 0
        for rank in other:
            if rank > 10:
                score += 10
            else:
                score += rank
        
        if not aces:
            scores.add(score)
        
        # Handling the aces. Here I use itertools.product() to give 
        # me all the ways to score the aces. Zero is scored as one, 
        # and one is scored as eleven. It's a little convoluted, but 
        # I think it's easier to read than the recursion would be.
        else:
            products = product('01', repeat=len(aces))
            for item in products:
                score_aces = 0
                for ace in item:
                    if ace == '0':
                        score_aces += 1
                    else:
                        score_aces += 11
                scores.add(score + score_aces)
        
        # Return results.
        scores = list(scores)
        return sorted(scores)
    
    def can_split(self):
        """Determine whether the hand can be split."""
        if len(self) == 2 and self[0].rank == self[1].rank:
            return True
        return False
    
    def is_blackjack(self):
        """Determine whether the hand is a natural blackjack."""
        if len(self.cards) == 2:
            ranks = sorted([card.rank for card in self.cards])
            if ranks[0] == 1 and ranks[1] >= 10:
                return True
        return False
