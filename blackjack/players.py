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
from typing import Callable, Optional, Type
from types import MethodType

import mkname
from yadr import roll

from blackjack import willbet
from blackjack import willdoubledown as wdd
from blackjack import willhit as wh
from blackjack import willinsure as wi
from blackjack import willsplit as ws
from blackjack.cards import Hand, HandTuple
from blackjack.model import Integer_, PosInt, Text, valfactory, valtupfactory


# Utility functions.
def undef_behavior(self, *args, **kwargs) -> None:
    """A default function for use by playerfactory when a behavior
    isn't defined.
    """
    raise TypeError('Behavior was not defined.')


def get_chips(bet):
    """Return the number of chips to give to a player.

    :param bet: The initial buyin for a game of blackjack.
    :return: The chips to give to the player.
    :rtype: int or float, depending on what bet was.
    """
    multiplier = choice(range(1, 21))
    return bet * multiplier


def make_name():
    """Create a name for a player."""
    config = mkname.get_config('')
    names = mkname.get_names_by_kind(kind='given')
    if roll('1d3') > 1:
        return mkname.build_compound_name(names)
    return mkname.select_name(names)


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
    def fromdict(cls, dict_: dict) -> 'Player':
        """Deserialize an instance of Player from a dictionary.

        :param dict_: A serialized instance of Player in a dictionary.
        :return: An instance of Player.
        :rtype: Player
        """
        names = [cls_.__name__ for cls_ in trusted_Players]
        if dict_['class'] not in names:
            msg = 'Wrong constructor for serialized class.'
            raise TypeError(msg)

        player = cls(dict_['hands'], dict_['name'], dict_['chips'])
        if 'insured' in dict_:
            player.insured = dict_['insured']
        methods = {
            'will_hit': wh.will_hits,
            'will_split': ws.will_splits,
            'will_double_down': wdd.will_double_downs,
            'will_insure': wi.will_insures,
            'will_bet': willbet.will_bets,
        }
        for meth in methods:
            fn_names = [fn.__name__ for fn in methods[meth]]
            try:
                index = fn_names.index(dict_[meth])
            except ValueError:
                msg = f'Invalid {meth} given. {dict_[meth]}'
                raise ValueError(msg)
            bound = MethodType(methods[meth][index], player)
            setattr(player, meth, bound)

        return player

    def __init__(self, hands: tuple = (),
                 name: str = 'Player',
                 chips: int = 0,
                 insured: int = 0) -> None:
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
        self.bet = 0

    def __str__(self):
        return self.name

    def __repr__(self):
        cls = self.__class__
        return f'{cls.__name__}[{self.name!r}]'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        self_dict = self._asdict()
        del self_dict['insured']
        other_dict = other._asdict()
        del other_dict['insured']

        return self_dict == other_dict

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
            'will_bet': self.will_bet.__name__,
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

    def will_bet(self, the_game) -> bool:
        raise NotImplementedError

    def will_buyin(self, hand: Hand, the_game) -> bool:
        raise NotImplementedError

    def will_double_down(self, hand: Hand, the_game) -> bool:
        raise NotImplementedError

    def will_hit(self, hand: Hand, the_game) -> bool:
        raise NotImplementedError

    def will_insure(self, the_game) -> bool:
        raise NotImplementedError

    def will_split(self, hand: Hand, the_game) -> bool:
        raise NotImplementedError


# Factory functions.
def playerfactory(
        name,
        will_bet: Optional[Callable] = undef_behavior,
        will_double_down: Optional[Callable] = undef_behavior,
        will_hit: Optional[Callable] = undef_behavior,
        will_insure: Optional[Callable] = undef_behavior,
        will_split: Optional[Callable] = undef_behavior
) -> type:
    """A factory function for Player subclasses."""
    attrs = {
        'will_bet': will_bet,
        'will_double_down': will_double_down,
        'will_hit': will_hit,
        'will_insure': will_insure,
        'will_split': will_split,
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
    cls: Type[Player] = classes[serial['class']]
    return cls.deserialize(s)


def make_player(chips=200, bet=None) -> Player:
    """Make a random player for a blackjack game."""
    if bet:
        chips = get_chips(bet)
    attrs = {
        'class': 'Player',
        'hands': (),
        'name': make_name(),
        'chips': chips,
        'will_hit': choice(wh.will_hits[2:]).__name__,
        'will_split': choice(ws.will_splits[2:]).__name__,
        'will_double_down': choice(wdd.will_double_downs[2:]).__name__,
        'will_insure': choice(wi.will_insures[2:]).__name__,
        'will_bet': choice(willbet.will_bets[2:]).__name__,
    }
    player = Player.fromdict(attrs)
    return player


# Player special case subclasses.
Dealer = playerfactory(
    'Dealer',
    will_bet=willbet.will_bet_dealer,
    will_double_down=wdd.will_double_down_dealer,
    will_hit=wh.will_hit_dealer,
    will_insure=wi.will_insure_dealer,
    will_split=ws.will_split_dealer
)
UserPlayer = playerfactory(
    'UserPlayer',
    will_bet=willbet.will_bet_user,
    will_double_down=wdd.will_double_down_user,
    will_hit=wh.will_hit_user,
    will_insure=wi.will_insure_user,
    will_split=ws.will_split_user
)


# Example player subclasses.
AutoPlayer = playerfactory(
    'AutoPlayer',
    will_bet=willbet.will_bet_max,
    will_double_down=wdd.will_double_down_always,
    will_hit=wh.will_hit_dealer,
    will_insure=wi.will_insure_always,
    will_split=ws.will_split_always
)
BetterPlayer = playerfactory(
    'BetterPlayer',
    will_bet=willbet.will_bet_min,
    will_double_down=wdd.will_double_down_recommended,
    will_hit=wh.will_hit_recommended,
    will_insure=wi.will_insure_never,
    will_split=ws.will_split_recommended
)
NeverPlayer = playerfactory(
    'NeverPlayer',
    will_bet=willbet.will_bet_never,
    will_double_down=wdd.will_double_down_never,
    will_hit=wh.will_hit_never,
    will_insure=wi.will_insure_never,
    will_split=ws.will_split_never
)
RandomPlayer = playerfactory(
    'RandomPlayer',
    will_bet=willbet.will_bet_random,
    will_double_down=wdd.will_double_down_random,
    will_hit=wh.will_hit_random,
    will_insure=wi.will_insure_random,
    will_split=ws.will_split_random
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
