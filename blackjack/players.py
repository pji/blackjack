"""
players
~~~~~~~

The module contains the basic classes used by blackjack for handling 
players, including the dealer.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from functools import partial
from json import dumps, loads
from random import choice
from typing import Callable
from types import MethodType

from blackjack.cards import Hand, HandTuple
from blackjack.model import Integer_, PosInt, Text, valfactory, valtupfactory
from blackjack.willbuyin import (will_buyin_dealer, 
                                 will_buyin_always, 
                                 will_buyin_never, 
                                 will_buyin_random, 
                                 will_buyins)
from blackjack.willdoubledown import (will_double_down_user, 
                                      will_double_down_dealer, 
                                      will_double_down_always, 
                                      will_double_down_never, 
                                      will_double_down_random, 
                                      will_double_down_recommended, 
                                      will_double_downs)
from blackjack.willhit import (will_hit_user, 
                               will_hit_dealer, 
                               will_hit_never, 
                               will_hit_random, 
                               will_hit_recommended,
                               will_hits)
from blackjack.willinsure import (will_insure_user, 
                                  will_insure_dealer, 
                                  will_insure_always, 
                                  will_insure_never, 
                                  will_insure_random, 
                                  will_insures)
from blackjack.willsplit import (will_split_user, 
                                 will_split_dealer, 
                                 will_split_always, 
                                 will_split_never, 
                                 will_split_random, 
                                 will_split_recommended, 
                                 will_splits)


# Popular baby names from specific years taken from "Official US List" 
# from babycenter.com.
NAMES = [
    # 2019
    'Sophia', 'Olivia', 'Emma', 'Ava', 'Aria', 'Isabella', 'Amelia', 
    'Mia', 'Riley', 'Aaliyah', 'Liam', 'Jackson', 'Noah', 'Aiden', 
    'Grayson', 'Caden', 'Lucas', 'Elijah', 'Oliver', 'Mason', 
    
    # 1996
    'Emily', 'Jessica', 'Ashley', 'Sarah', 'Samantha', 'Taylor', 'Hannah', 
    'Alexis', 'Rachel', 'Elizabeth', 'Michael', 'Matthew', 'Jacob', 
    'Christopher', 'Joshua', 'Nicholas', 'Tyler', 'Brandon', 'Austin', 
    'Andrew',
    
    # 1976
    'Jennifer', 'Amy', 'Melissa', 'Heather', 'Angela', 'Michelle', 
    'Kimberly', 'Jessica', 'Lisa', 'Amanda', 'Michael', 'Jason', 
    'Christopher', 'David', 'James', 'John', 'Robert', 'Brian', 
    'Matthew', 'Daniel', 
    
    # 1956
    'Mary', 'Debra', 'Linda', 'Deborah', 'Susan', 'Patricia', 'Karen', 
    'Cynthia', 'Barbara', 'Donna', 'Michael', 'James', 'Robert', 
    'David', 'John', 'William', 'Richard', 'Mark', 'Thomas', 'Steven',
]


# Utility functions.
def get_chips(bet):
    """Return the number of chips to give to a player.
    
    :param bet: The initial buyin for a game of blackjack.
    :return: The chips to give to the player.
    :rtype: int or float, depending on what bet was.
    """
    multiplier = choice(range(1, 21))
    return bet * multiplier

def get_name():
    """Return a random name."""
    return choice(NAMES)

def name_builder(start:str, end:str) -> str:
    """Given three strings, return a string that combines them.
    
    :param beginning: The string to use for the beginning of the 
        result.
    :param middle: The string to use for the middle of the result.
    :param end: The string to use for the end of the result.
    :return: The new string.
    :rtype: str
    """
    vowels = 'aeiouy'
    consonants = 'bcdfghjklmnpqrstvwxz'
    start = start.lower()
    end = end.lower()
    
    def get_change_index(s:str, letters):
        index = 1
        while index < len(s) and s[index] in letters:
            index += 1
        return index
    
    name = ''
    if end[0] not in vowels and start[0] not in vowels:
        index_start = get_change_index(start, consonants)
        index_end = get_change_index(end, consonants)
        name = start[0:index_start] + end[index_end:]
    elif end[0] in vowels and start[0] not in vowels:
        index_start = get_change_index(start, consonants)
        name = start[0:index_start] + end
    elif end[0] in vowels and start[0] in vowels:
        index_start = get_change_index(start, vowels)
        index_end = get_change_index(end, vowels)
        name = start[0:index_start] + end[index_end:]
    else:
        index_start = get_change_index(start, vowels)
        name = start[0:index_start] + end
    return name[0].upper() + name[1:]


# Base class.
class Player:
    """A blackjack player."""
    hands = HandTuple('hand')
    name = Text('name')
    chips = Integer_('chips')
    insured = PosInt('insured')
    
    @classmethod
    def deserialize(cls, s):
        """When called with a Player object serialized as a JSON 
        string, return the deserialized Player object.
        """
        serial = loads(s)
        serial['hands'] = [Hand.deserialize(hand) for hand in serial['hands']]
        return cls.fromdict(serial)
    
    @classmethod
    def fromdict(cls, dict_:dict) -> 'Player':
        """Deserialize an instance of Player from a dictionary.
        
        :param dict_: A serialized instance of Player in a dictionary. 
        :return: An instance of Player.
        :rtype: Player
        """
        names = [cls_.__name__ for cls_ in trusted_Players]
        if dict_['class'] not in names:
            msg('Wrong constructor for serialized class.')
            raise TypeError(msg)
        
        player = cls(dict_['hands'], dict_['name'], dict_['chips'])
        methods = {
            'will_hit': will_hits,
            'will_split': will_splits,
            'will_buyin': will_buyins,
            'will_double_down': will_double_downs,
            'will_insure': will_insures,
        }
        for meth in methods:
            fn_names = [fn.__name__ for fn in methods[meth]]
            try:
                index = fn_names.index(dict_[meth])
            except ValueError:
                msg = f'Invalid {meth} given.'
                raise ValueError(msg)
            bound = MethodType(methods[meth][index], player)
            setattr(player, meth, bound)
        
        return player
    
    def __init__(self, hands: tuple = (), name: str = 'Player', 
                 chips: int = 0) -> None:
        """Initialize and instance of the class.
        
        :param hands: The player's hands of blackjack.
        :param name: The player's name.
        :param chips: The chips the player has for betting.
        :return: None.
        :rtype: None.
        """
        self.hands = hands
        self.name = name
        if not chips:
            chips = 0
        self.chips = chips
        self.insured = 0
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        cls = self.__class__
        return f'{cls.__name__}[{self.name!r}]'
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        
        return (
            self.hands == other.hands
            and self.name == other.name
            and self.chips == other.chips 
            and self.will_buyin.__name__ == other.will_buyin.__name__
            and self.will_double_down.__name__ == other.will_double_down.__name__
            and self.will_hit.__name__ == other.will_hit.__name__
            and self.will_insure.__name__ == other.will_insure.__name__
            and self.will_split.__name__ == other.will_split.__name__
        )
    
    def __format__(self, format_spec):
        return self.name.__format__(format_spec)
    
    def _asdict(self):
        """Return a dictionary that is a representation of the 
        class.
        """
        return {
            'class': self.__class__.__name__,
            'chips': self.chips,
            'hands': self.hands,
            'insured': self.insured,
            'name': self.name,
            'will_buyin': self.will_buyin.__name__,
            'will_double_down': self.will_double_down.__name__,
            'will_hit': self.will_hit.__name__,
            'will_insure': self.will_insure.__name__,
            'will_split': self.will_split.__name__,
        }
    
    def serialize(self):
        """Return the object serialized as a JSON string."""
        serial = self._asdict()
        serial['hands'] = [hand.serialize() for hand in serial['hands']]
        return dumps(serial)
    
    def will_hit(self, hand:Hand, the_game) -> bool:
        raise NotImplementedError
    
    def will_split(self, hand:Hand, the_game) -> bool:
        raise NotImplementedError
    
    def will_buyin(self, hand:Hand, the_game) -> bool:
        raise NotImplementedError
    
    def will_double_down(self, hand:Hand, the_game) -> bool:
        raise NotImplementedError
    
    def will_insure(self, hand:Hand, the_game) -> bool:
        raise NotImplementedError


# Factory functions.
def playerfactory(name, will_hit_fn, will_split_fn, will_buyin_fn, 
                  will_double_down, will_insure) -> type:
    """A factory function for Player subclasses."""
    attrs = {
        'will_hit': will_hit_fn,
        'will_split': will_split_fn,
        'will_buyin': will_buyin_fn,
        'will_double_down': will_double_down,
        'will_insure': will_insure,
    }
    return type(name, (Player,), attrs)


def restore_player(s: str) -> Player:
    """Given a serialized player object, restore it as the proper 
    class.
    """
    # There has got to be a better way to do this.
    classes = {
        'Player': Player,
        'Dealer': Dealer,
        'AutoPlayer': AutoPlayer,
        'BetterPlayer': BetterPlayer,
        'UserPlayer': UserPlayer,
    }
    serial = loads(s)
    cls = classes[serial['class']]
    return cls.deserialize(s)


def make_player(chips=200, bet=None) -> Player:
    """Make a random player for a blackjack game."""
    def make_name() -> str:
        if 0 != choice(range(3)):
            return get_name()
        else:
            return name_builder(get_name(), get_name())
    
    if bet:
        chips = get_chips(bet)
    attrs = {
        'class': 'Player',
        'hands': (),
        'name': make_name(),
        'chips': chips,
        'will_hit': choice(will_hits[2:]).__name__,
        'will_split': choice(will_splits[2:]).__name__,
        'will_buyin': choice(will_buyins[1:]).__name__,
        'will_double_down': choice(will_double_downs[2:]).__name__,
        'will_insure': choice(will_insures[2:]).__name__,
    }
    player = Player.fromdict(attrs)
    return player


# Player subclasses.
Dealer = playerfactory(
    'Dealer', 
    will_hit_dealer, 
    will_split_dealer, 
    will_buyin_dealer, 
    will_double_down_dealer, 
    will_insure_dealer
)
AutoPlayer = playerfactory(
    'AutoPlayer', 
    will_hit_dealer, 
    will_split_always,
    will_buyin_always, 
    will_double_down_always, 
    will_insure_always
)
BetterPlayer = playerfactory(
    'BetterPlayer', 
    will_hit_recommended, 
    will_split_recommended, 
    will_buyin_always, 
    will_double_down_recommended, 
    will_insure_never
)
NeverPlayer = playerfactory(
    'NeverPlayer', 
    will_hit_never, 
    will_split_never, 
    will_buyin_never, 
    will_double_down_never, 
    will_insure_never
)
RandomPlayer = playerfactory(
    'RandomPlayer',
    will_hit_random,
    will_split_random,
    will_buyin_random,
    will_double_down_random,
    will_insure_random
)
UserPlayer = playerfactory(
    'UserPlayer', 
    will_hit_user, 
    will_split_user, 
    will_buyin_always, 
    will_double_down_user, 
    will_insure_user
)


# List of trusted Player subclasses for deserialization:
trusted_Players = [
    Player, 
    Dealer, 
    AutoPlayer, 
    BetterPlayer, 
    NeverPlayer,
    UserPlayer,
]


# Player validation functions.
def validate_player_or_none(self, value):
    """Validate Players and None."""
    if not isinstance(value, (Player, type(None))):
        reason = 'not an instance of Player'
        raise ValueError(self.msg.format(reason))
    return value


# Player validating descriptors.
ValidPlayer = valfactory(
    'ValidPlayer', 
    validate_player_or_none, 
    'Invalid player ({}).'
)
ValidPlayers = valtupfactory(
    'ValidPlayers', 
    validate_player_or_none, 
    'Invalid contents ({}).'
)