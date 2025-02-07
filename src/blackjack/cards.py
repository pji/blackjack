"""
cards
~~~~~

The module contains the classes for working with cards and decks
of cards.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from collections import OrderedDict
from collections.abc import Iterable, MutableSequence, Sequence
from copy import copy, deepcopy
from dataclasses import dataclass, field
from functools import total_ordering
from itertools import product
from json import dumps, loads
from random import randrange, shuffle

from blackjack.model import Boolean, Integer_, PosInt, valfactory


# Global values.
UP = True
DOWN = False
RANKS = list(range(1, 14))
RANK_TRANSLATION = {
    1: 'A',
    11: 'J',
    12: 'Q',
    13: 'K',
}
SUITS = OrderedDict([
    ('clubs', '♣'),
    ('diamonds', '♦'),
    ('hearts', '♥'),
    ('spades', '♠'),
])
CARD_BACK = '\u2500'


# Validator functions.
def validate_cardtuple(self, value: 'Sequence[Card]') -> 'tuple[Card, ...]':
    """Validate a sequence of cards.

    :param value: The value to validate.
    :returns: A :class:`tuple` of :class:`blackjack.cards.Card` objects.
    :rtype: tuple
    """
    # Normalize the sequence to a tuple.
    try:
        normal = tuple(value)

    # Raise a VakueError if the value can't be normalized to a tuple.
    except TypeError:
        reason = 'cannot be made a tuple'
        raise ValueError(self.msg.format(reason))

    # Ensure each item in the normalized sequence is a Card object.
    else:
        for item in normal:
            if not isinstance(item, Card):
                reason = 'contains non-card'
                raise ValueError(self.msg.format(reason))
        return normal


def validate_deck(self, value: 'Deck') -> 'Deck':
    """Validate a deck.

    :param value: The value to validate.
    :returns: A :class:`blackjack.cards.Deck` object.
    :rtype: blackjack.cards.Deck
    """
    if isinstance(value, Deck):
        return value
    reason = 'object is not a Deck'
    raise ValueError(self.msg.format(reason))


def validate_handtuple(self, value: 'Sequence[Hand]') -> tuple:
    """Validate a sequence of cards."""
    if value is None:
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
@total_ordering
class Card:
    """A playing card for the game of blackjack.

    :param rank: (Optional.) The rank (number value) of the card.
    :param suit: (Optional.) The suit of the card.
    :param facing: (Optional.) Whether the card is face up. True
        is face up. False is face down.
    :return: A :class:`blackjack.cards.Card` object.
    :rtype: blackjack.cards.Card

    Usage::

        >>> # Create a new card.
        >>> card = Card(7, 'hearts', UP)
        >>> card
        Card(rank=7, suit='hearts', facing=True)
        >>>
        >>> # Card ranks are ints, so here is a queen of diamonds.
        >>> card = Card(12, 'diamonds', UP)
        >>> card
        Card(rank=12, suit='diamonds', facing=True)
        >>>
        >>> # Converting it to a str shows that it's a queen.
        >>> str(card)
        'Q♦'
        >>>
        >>> # Cards can be face up or face down, which changes the str.
        >>> card = Card(12, 'diamonds', DOWN)
        >>> str(card)
        '──'
        >>>
        >>> # You can also compare them. The comparison only looks at
        >>> # both rank and suit.
        >>> card_a = Card(8, 'spades', UP)
        >>> card_b = Card(8, 'diamonds', UP)
        >>> card_c = Card(11, 'clubs', UP)
        >>> card_a == card_c
        False
        >>> card_a == card_b
        False
        >>> card_a < card_c
        True
    """
    rank = Rank('rank')
    suit = Suit('suit')
    facing = Boolean('facing')

    # Class methods.
    @classmethod
    def deserialize(cls, s: str) -> 'Card':
        """Deserialize an instance of the class.

        :param s: An object serialized as a json string.
        :return: An instance of the class.
        :type: Card

        Usage::

            >>> json = '["Card", 11, "clubs", true]'
            >>> Card.deserialize(json)
            Card(rank=11, suit='clubs', facing=True)
        """
        args = loads(s)
        if args[0] == cls.__name__:
            return cls(*args[1:])
        else:
            msg = 'Serialized object was not a Card object.'
            raise TypeError(msg)

    # Magic methods.
    def __init__(
        self,
        rank: int = 11,
        suit: str = 'spades',
        facing: bool = UP
    ) -> None:
        """Initialize an instance of the class."""
        self.rank = rank
        self.suit = suit
        self.facing = facing

    def __repr__(self):
        cls = self.__class__
        tmp = '{}(rank={}, suit={!r}, facing={})'
        return tmp.format(cls.__name__, self.rank, self.suit, self.facing)

    def __str__(self):
        rank = CARD_BACK
        suit = CARD_BACK
        if self.facing == UP:
            rank = self.rank
            if rank in RANK_TRANSLATION:
                rank = RANK_TRANSLATION[rank]
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

    # Public methods.
    def astuple(self) -> tuple[str, int, str, bool]:
        """Return the card's attributes for serialization.

        :returns: A :class:`tuple` object.
        :rtype: tuple

        Usage::

            >>> card = Card(11, 'clubs')
            >>> card.astuple()
            ('Card', 11, 'clubs', True)
        """
        return (self.__class__.__name__, self.rank, self.suit, self.facing)

    def flip(self) -> None:
        """Flip the facing of the card.

        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> card = Card(11, 'clubs', DOWN)
            >>> str(card)
            '──'
            >>> card.flip()
            >>> str(card)
            'J♣'
            >>> card.flip()
            >>> str(card)
            '──'
        """
        self.facing = not self.facing

    def serialize(self) -> str:
        """Serialize the object as JSON.

        :returns: A :class:`str` object.
        :rtype: str

        Usage::

            >>> card = Card(11, 'clubs')
            >>> card.serialize()
            '["Card", 11, "clubs", true]'
        """
        return dumps(self.astuple())


class Pile(MutableSequence):
    """A generic pile of cards.

    :param cards: (Optional.) A list containing the cards held by
        the deck.
    :param _iter_index: (Optional.) The current index when iterating
        through the pile. It's intended to be used only when deserializing
        a pile. Defaults to 0.
    :return: A :class:`blackjack.cards.Pile` object.
    :rtype: blackjack.cards.Pile

    Usage::

        >>> # Creating a pile with cards.
        >>> c1 = Card(11, 'spades')
        >>> c2 = Card(6, 'hearts')
        >>> c3 = Card(4, 'diamonds')
        >>> pile = Pile([c1, c2, c3])
        >>> pile
        Pile['J♠', '6♥', '4♦']
        >>>
        >>> # You can get the number of cards in the pile.
        >>> len(pile)
        3
        >>>
        >>> # It works as an iterator.
        >>> for card in pile:
        ...     print(card)
        ...
        J♠
        6♥
        4♦
    """
    _iter_index = Integer_('_iter_index')
    cards = CardTuple('cards')

    @classmethod
    def deserialize(cls, s: str) -> 'Pile':
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

    def __init__(
        self,
        cards: Sequence[Card] | None = None,
        _iter_index: int = 0
    ) -> None:
        """Initialize and instance of the class."""
        self._iter_index = _iter_index
        if not cards:
            cards = []
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
        if isinstance(key, int):
            return self.cards.__getitem__(key)
        elif isinstance(key, slice):
            cards = self.cards[key]
            return self.__class__(cards)

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

    # Utility methods.
    def asdict(self) -> dict:
        """Return a version of the object serialized as a dictionary.

        :returns: A :class:`dict` object.
        :rtype: dict

        Usage::

            >>> c1 = Card(11, 'spades')
            >>> c2 = Card(10, 'hearts')
            >>> pile = Pile([c1, c2])
            >>>
            >>> # Serialize the pile.
            >>> pile.serialize()                    # doctest: +ELLIPSIS
            '{"class": "Pile", "_iter_index": 0, "car...true]"]}'
        """
        return {
            'class': self.__class__.__name__,
            '_iter_index': self._iter_index,
            'cards': [card.serialize() for card in self.cards]
        }

    def append(self, item: Card) -> None:
        """Add a card to the end of the pile.

        :param item: The card to add to the pile.
        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> c1 = Card(11, 'spades')
            >>> c2 = Card(10, 'hearts')
            >>> pile = Pile([c1, c2])
            >>>
            >>> # Add a new card to the pile.
            >>> c3 = Card(1, 'clubs')
            >>> pile.append(c3)
            >>> pile
            Pile['J♠', '10♥', 'A♣']
        """
        cards = list(self.cards)
        cards.append(item)
        self.cards = tuple(cards)

    def copy(self) -> 'Pile':
        """Return a copy of the Deck object.

        :returns: A :class:`blackjack.cards.Pile` object.
        :rtype: blackjack.cards.Pile

        Usage::

            >>> c1 = Card(11, 'spades')
            >>> c2 = Card(10, 'hearts')
            >>> pile = Pile([c1, c2])
            >>>
            >>> # Copy the pile.
            >>> new = pile.copy()
            >>>
            >>> # Copies are equivalent.
            >>> new == pile
            True
            >>>
            >>> # But they aren't the same object.
            >>> new is pile
            False
        """
        return copy(self)

    def extend(self, iterable: Iterable[Card]) -> None:
        """Append all items from the given iterable.

        :param iterable: The :class:`Iterable` to add to the pile.
        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> c1 = Card(11, 'spades')
            >>> c2 = Card(10, 'hearts')
            >>> pile1 = Pile([c1, c2])
            >>>
            >>> c3 = Card(1, 'spades')
            >>> c4 = Card(11, 'clubs')
            >>> pile2 = Pile([c3, c4])
            >>>
            >>> # Add pile2 to the end of pile1.
            >>> pile1.extend(pile2)
            >>> pile1
            Pile['J♠', '10♥', 'A♠', 'J♣']
        """
        cards = list(self.cards)
        cards.extend(iterable)
        self.cards = tuple(cards)

    def serialize(self) -> str:
        """Return the object serialized as a JSON string.

        :returns: A :class:`str` object.
        :rtype: str

        Usage::

            >>> c1 = Card(11, 'spades')
            >>> c2 = Card(10, 'hearts')
            >>> pile = Pile([c1, c2])
            >>>
            >>> # Serialize the pile.
            >>> pile.serialize()                # doctest: +ELLIPSIS
            '{"class": "Pile", "_iter_index": 0,... true]"]}'
        """
        return dumps(self.asdict())


class Deck(Pile):
    """A deck of playing cards for blackjack.

    :param cards: (Optional.) The cards to add to the deck. Defaults
        to `None`.
    :param size: (Optional.) The number of 52 card decks in the full
        deck. Defaults to `1`.
    :param _iter_index: (Optional.) The current index when iterating
        through the pile. It's intended to be used only when deserializing
        a pile. Defaults to 0.
    :returns: A :class:`blackjack.cards.Deck` object.
    :rtype: blackjack.cards.Deck

    Usage::

        >>> cards = [Card(r, s) for s, r in product(SUITS, RANKS)]
        >>> deck = Deck(cards, size=1)
        >>> deck                                    # doctest: +ELLIPSIS
        Deck['A♣', '2♣', '3♣', '4♣', '5♣', '6♣', '7♣', '8♣', '9♣',... 'K♠']
    """
    size = PosInt('size')

    # Class methods.
    @classmethod
    def build(cls, num_decks: int = 1):
        """(Class method.) Create a Deck object that is populated
        with cards. The cards in the deck are all face down.

        :param num_decks: (Optional.) The number of standard decks to
            use when constructing the deck.
        :return: A :class:`blackjack.cards.Deck` object.
        :rtype: blackjack.cards.Deck

        Usage::

            >>> # Create a deck containing three standard 52-card decks.
            >>> deck = Deck.build(3)
            >>>
            >>> # It is made of three decks.
            >>> deck.size
            3
            >>>
            >>> # Thee decks has 52 * 3 = 156 cards.
            >>> len(deck)
            156
        """
        ranks = reversed(RANKS)
        std_deck = [Card(r, s, DOWN) for s, r in product(SUITS, ranks)]
        cards = []
        for i in range(num_decks):
            cards.extend(deepcopy(std_deck))
        return cls(cards, num_decks)

    # Magic methods.
    def __init__(
        self,
        cards: Sequence[Card] | None = None,
        size: int = 1,
        *args, **kwargs
    ) -> None:
        super().__init__(cards, *args, **kwargs)
        self.size = size

    # Public methods.
    def asdict(self) -> dict[str, str | int | list[str]]:
        """Return the object as a dictionary.

        :returns: A :class:`dict` object.
        :rtype: dict

        Usage::

            >>> deck = Deck.build(1)
            >>>
            >>> # Serialize the deck as a dict.
            >>> deck.asdict()                   # doctest: +ELLIPSIS
            {'class': 'Deck', '_iter_index': 0, ... 'size': 1}
        """
        serial = super().asdict()
        serial['size'] = self.size
        return serial

    def draw(self) -> Card:
        """Draw the top card from the deck.

        NOTE: Due to how lists work, it is more efficient for the top
        of the deck to be index -1 rather than index 0, even though
        this is counterintuitive.

        :return: A :class:`blackjack.cards.Card` object.
        :rtype: blackjack.cards.Card

        Usage::

            >>> deck = Deck.build(1)
            >>>
            >>> # Draw a card.
            >>> deck.draw()
            Card(rank=1, suit='spades', facing=False)
        """
        return self.pop()

    def shuffle(self) -> None:
        """Randomize the order of the deck.

        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> deck = Deck.build(1)
            >>>
            >>> # Before the shuffle the cards are all in order.
            >>> for card in deck[:5]:
            ...     repr(card)
            ...
            "Card(rank=13, suit='clubs', facing=False)"
            "Card(rank=12, suit='clubs', facing=False)"
            "Card(rank=11, suit='clubs', facing=False)"
            "Card(rank=10, suit='clubs', facing=False)"
            "Card(rank=9, suit='clubs', facing=False)"
            >>>
            >>> # Shuffling changes the order.
            >>> deck.shuffle()
            >>> for card in deck[:5]:
            ...     repr(card)
            ...
            "Card(rank=10, suit='hearts', facing=False)"
            "Card(rank=1, suit='hearts', facing=False)"
            "Card(rank=7, suit='spades', facing=False)"
            "Card(rank=4, suit='clubs', facing=False)"
            "Card(rank=7, suit='hearts', facing=False)"
        """
        cards = list(self.cards)
        shuffle(cards)
        self.cards = tuple(cards)

    def random_cut(self) -> None:
        """Remove the last 60-75 cards from the deck. This is done
        before a round of blackjack begins to make it harder to
        count cards.

        :returns: `None`.
        :rtype: NoneType

        Usage::

            >>> # Seeding the random number generator to ensure repeatability
            >>> # for testing. Don't do this when not testing.
            >>> from random import seed
            >>> seed('spam')
            >>>
            >>> # Create the deck.
            >>> deck = Deck.build(3)
            >>> len(deck)
            156
            >>> deck[0]
            Card(rank=13, suit='clubs', facing=False)
            >>>
            >>> # Cut the deck.
            >>> deck.random_cut()
            >>> len(deck)
            93
            >>> deck[0]
            Card(rank=2, suit='clubs', facing=False)
        """
        num = randrange(60, 76)
        self.cards = self.cards[num:]


class Hand(Pile):
    """A hand of blackjack.

    NOTE: Five card charlie (winning if you get five cards without
    busting) is a house rule. This implementation is based on the
    Bicycle rules for Blackjack at bicyclecards.com, so it doesn't
    implement that rule.

    :param cards: (Optional.) The cards to add to the deck. Defaults
        to `None`.
    :param _iter_index: (Optional.) The current index when iterating
        through the pile. It's intended to be used only when deserializing
        a pile. Defaults to 0.
    :param doubled_down: (Optional.) Whether the hand has been doubled
        down. Defaults to `False`.
    :returns: A :class:`blackjack.cards.Hand` object.
    :rtype: blackjack.cards.Hand

    Usage::

        >>> # Create a hand.
        >>> c1 = Card(1, 'hearts')
        >>> c2 = Card(11, 'spades')
        >>> cards = [c1, c2]
        >>> hand = Hand(cards)
        >>> hand
        Hand['A♥', 'J♠']
    """
    doubled_down = Boolean('doubled_down')

    # Magic methods.
    def __init__(self, *args, doubled_down: bool = False, **kwargs) -> None:
        """Initialize an instance of the class."""
        super().__init__(*args, **kwargs)
        self.doubled_down = doubled_down

    def __format__(self, format_spec):
        value = self.__str__()
        return value.__format__(format_spec)

    def __str__(self):
        return ' '.join(str(card) for card in self.cards)

    # Properties.
    @property
    def can_split(self) -> bool:
        """Determine whether the hand can be split."""
        if len(self) == 2 and self[0].rank == self[1].rank:
            return True
        return False

    @property
    def is_blackjack(self) -> bool:
        """Determine whether the hand is a natural blackjack."""
        if len(self.cards) == 2:
            ranks = sorted([card.rank for card in self.cards])
            if ranks[0] == 1 and ranks[1] >= 10:
                return True
        return False

    @property
    def is_bust(self) -> bool:
        """Return whether the hand is bust."""
        scores = [score for score in self.score() if score <= 21]
        if not scores:
            return True
        return False

    # Public methods.
    def asdict(self) -> dict[str, str | int | list[str]]:
        """Return the object serialized as a dictionary.

        :returns: A :class:`dict` object.
        :rtype: dict

        Usage::

            >>> cards = [Card(1, 'hearts'), Card(11, 'spades')]
            >>> hand = Hand(cards)
            >>>
            >>> # Serialize the hand.
            >>> hand.asdict()                   # doctest: +ELLIPSIS
            {'class': 'Hand', '_iter_index': 0,... False}
        """
        serial = super().asdict()
        serial['doubled_down'] = self.doubled_down
        return serial

    def score(self) -> list[int]:
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
        result = list(scores)
        return sorted(result)

    def split(self):
        """Split the hand."""
        if not self.can_split:
            msg = 'Hand cannot be split.'
            raise ValueError(msg)
        hand = sorted(self.cards)
        return (
            Hand([hand[0],]),
            Hand([hand[1],]),
        )
