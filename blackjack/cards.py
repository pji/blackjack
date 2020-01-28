"""
cards
~~~~~

The module contains the basic classes used by blackjack for handling 
cards.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from collections import OrderedDict
from collections.abc import MutableSequence
from copy import copy, deepcopy
from itertools import product
from json import dumps, loads
from random import randrange, shuffle
from typing import Sequence

from blackjack.model import Boolean, Integer_, PosInt, valfactory

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
def validate_cardtuple(self, value: 'Sequence[Card]') -> tuple:
    """Validate a sequence of cards."""
    try:
        normal = tuple(value)
    except TypeError:
        reason = 'cannot be made a tuple'
        raise ValueError(self.msg.format(reason))
    else:
        for item in normal:
            if not isinstance(item, Card):
                reason = 'contains non-card'
                raise ValueError(self.msg.format(reason))
        return normal

def validate_deck(self, value: 'Deck') -> 'Deck':
    """Validate a deck."""
    if isinstance(value, Deck):
        return value
    reason = 'object is not a Deck'
    raise ValueError(self.msg.format(reason))

def validate_handtuple(self, value: 'Sequence[Hand]') -> tuple:
    """Validate a sequence of cards."""
    if value == None:
        return value
    try:
        normal = tuple(value)
    except TypeError:
        reason = 'cannot be made a tuple'
        raise ValueError(self.msg.format(reason))
    else:
        for item in normal:
            if not isinstance(item, Hand):
                reason = 'contains non-hand'
                raise ValueError(self.msg.format(reason))
        return normal

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
CardTuple = valfactory('CardTuple', validate_cardtuple, 'Invalid ({}).')
DeckObj = valfactory('DeckObj', validate_deck, 'Invalid deck ({}).')
HandTuple = valfactory('HandTuple', validate_handtuple, 'Invalid ({}).')
Rank = valfactory('Rank', validate_rank, 'Invalid rank ({}).')
Suit = valfactory('Suit', validate_suit, 'Invalid suit ({}).')


# Common classes.
class Card:
    """A playing card for the game of blackjack."""
    rank = Rank('rank')
    suit = Suit('suit')
    facing = Boolean('facing')
    
    @classmethod
    def deserialize(cls, s:str) -> 'Card':
        """Deserialize an instance of the class.
        
        :param s: An object serialized as a json string.
        :return: An instance of the class.
        :type: Card
        """
        args = loads(s)
        if args[0] == cls.__name__:
            return cls(*args[1:])
        else:
            msg = 'Serialized object was not a Card object.'
            raise TypeError(msg)
    
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
    
    def __lt__(self, other):
        cls = self.__class__
        if not isinstance(other, cls):
            return NotImplemented
        if self.rank < other.rank:
            return True
        if self.rank == other.rank:
            suits = list(SUITS.keys())
            if suits.index(self.suit) < suits.index(other.suit):
                return True
        return False
    
    def _astuple(self) -> tuple:
        """Return the card's attributes for serialization."""
        return (self.__class__.__name__, self.rank, self.suit, self.facing)
    
    def flip(self):
        """Flip the facing of the card."""
        self.facing = not self.facing
    
    def serialize(self) -> str:
        """Serialize the object as JSON."""
        return dumps(self._astuple())


class Pile(MutableSequence):
    """A generic pile of cards."""
    _iter_index = Integer_('_iter_index')
    cards = CardTuple('cards')
    
    @classmethod
    def deserialize(cls, s:str) -> 'Pile':
        """Deserialize an instance of the class.
        
        :param s: A Pile object serialized as a json string.
        :return: The deserialized object.
        :rtype: Pile
        """
        serial = loads(s)
        if serial['class'] == cls.__name__:
            kwargs = {key: serial[key] for key in serial if key != 'class'}
            kwargs['cards'] = [Card.deserialize(card) 
                               for card in kwargs['cards']]
            return cls(**kwargs)
        else:
            msg = 'Serialized object was not a Pile object.'
            raise TypeError(msg)
    
    def __init__(self, cards: list = None, _iter_index: int = 0) -> None:
        """Initialize and instance of the class.
        
        :param cards: (Optional.) A list containing the cards held by 
            the deck.
        :return: None
        :rtype: None
        """
        self._iter_index = _iter_index
        if not cards:
            cards = ()
        self.cards = cards
    
    def __eq__(self, other):
        if isinstance(other, Pile):
            return self.cards == other.cards
        return NotImplemented
    
    def __repr__(self):
        cls = self.__class__.__name__
        return cls + str([str(card) for card in self.cards])
    
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
        cards = list(self.cards)
        cards.__setitem__(key, value)
        self.cards = tuple(cards)
    
    def __delitem__(self, key):
        cards = list(self.cards)
        cards.__delitem__(key)
        self.cards = tuple(cards)
    
    def insert(self, key, item):
        cards = list(self.cards)
        cards.insert(key, item)
        self.cards = cards
    
    #Utility methods.
    def _asdict(self) -> dict:
        """Return a version of the object serialized as a dictionary."""
        return {
            'class': self.__class__.__name__,
            '_iter_index': self._iter_index,
            'cards': [card.serialize() for card in self.cards]
        }
    
    def copy(self):
        """Return a copy of the Deck object."""
        return copy(self)
    
    def extend(self, iterable):
        """Append all items from the given iterable."""
        cards = list(self.cards)
        cards.extend(iterable)
        self.cards = tuple(cards)
    
    def serialize(self) -> str:
        """Return the object serialized as a JSON string."""
        return dumps(self._asdict())


class Deck(Pile):
    """A deck of playing cards for blackjack."""
    size = PosInt('size')
    
    def __init__(self, cards: list = None, size: int = 1) -> None:
        super().__init__(cards)
        self.size = size
    
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
        d.size = num_decks
        ranks = reversed(RANKS)
        std_deck = [Card(rank, suit, DOWN) for suit, rank 
                    in product(SUITS, ranks)]
        for i in range(d.size):
            d.extend(deepcopy(std_deck))
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
        cards = list(self.cards)
        shuffle(cards)
        self.cards = tuple(cards)
    
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
    doubled_down = Boolean('doubled_down')
    
    def __init__(self, *args, **kwargs) -> None:
        """Initialize an instance of the class."""
        super().__init__(*args, **kwargs)
        self.doubled_down = False
    
    def __format__(self, format_spec):
        value = self.__str__()
        return value.__format__(format_spec)
    
    def __str__(self):
        return ' '.join(str(card) for card in self.cards)
    
    def append(self, item):
        cards = list(self.cards)
        cards.append(item)
        self.cards = tuple(cards)
    
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
    
    def is_bust(self):
        """Return whether the hand is bust."""
        scores = [score for score in self.score() if score <= 21]
        if not scores:
            return True
        return False
    
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
    
    def split(self):
        """Split the hand."""
        if not self.can_split():
            msg = 'Hand cannot be split.'
            raise ValueError(msg)
        hand = sorted(self.cards)
        return (
            Hand([hand[0],]),
            Hand([hand[1],]),
        )
