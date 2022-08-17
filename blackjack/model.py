"""
model
~~~~~

The module contains the basic classes used to build blackjack's
data model.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from abc import ABC, abstractmethod
from typing import Union
from unicodedata import normalize
from typing import Any, Iterable, Optional, Sequence


# Base validation classes.
class _BaseDescriptor:
    """A basic data descriptor."""

    def __init__(self):
        cls = self.__class__
        self_hash = hash(self)
        self.storage_name = f'_{cls.__name__}#{self_hash}'

    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)

    def __get__(self, instance, owner):
        if instance is not None:
            return getattr(instance, self.storage_name)
        return self


class Validated(ABC, _BaseDescriptor):
    """A validating data descriptor."""
    msg = None

    def __init__(self, attr_name: str = None) -> None:
        """Initialize an instance of the class.

        :param attr_name: (Optional.) The name of the descriptor's
            protected attribute. If given, this is used to mangle
            the name of the key used to store the protected
            attribute's value.
        """
        super().__init__()
        if attr_name:
            cls = self.__class__
            self.storage_name = f'_{cls.__name__}__{attr_name}'

    def __repr__(self):
        cls = self.__class__.__name__
        return f'{cls}(storage_name={self.storage_name!r})'

    def __set__(self, instance, value):
        valid = self.validate(value)
        setattr(instance, self.storage_name, valid)

    @abstractmethod
    def validate(self, value):
        """Return the validated value or raise ValueError.

        :param value: The value to validate.
        :return: The canonicalized, normalized, validated value.
        :rtype: Varies.
        """


class ValidatedTuple(ABC, _BaseDescriptor):
    """A validating data descriptor for sequences."""
    msg = 'Invalid contents ({}).'

    def __init__(self, attr_name: str = None) -> None:
        """Initialize an instance of the class.

        :param attr_name: (Optional.) The name of the descriptor's
            protected attribute. If given, this is used to mangle
            the name of the key used to store the protected
            attribute's value.
        """
        super().__init__()
        if attr_name:
            cls = self.__class__
            self.storage_name = f'_{cls.__name__}__{attr_name}'

    def __repr__(self):
        cls = self.__class__.__name__
        return f'{cls}(storage_name={self.storage_name!r})'

    def __set__(self, instance, value):
        valid = self.validate_tuple(value)
        setattr(instance, self.storage_name, valid)

    def validate_tuple(self, seq:Iterable[Any]) -> tuple:
        """Return the validated sequence as a tuple or raise a
        relevant exception.

        :param seq: The sequence to validate.
        :return: The sequence as a tuple.
        :rtype: tuple
        """
        # We need to iterate on the passed value to validate its
        # contents. This could generate two types of TypeErrors:
        # TypeErrors from the value not being an iterator and
        # TypeErrors raised by the validate() method. Rather than
        # trying to parse the exception messages, we just test
        # up front if the passed value is an iterator.
        try:
            _ = seq.__iter__()
        except AttributeError:
            reason = 'Invalid sequence (not an iterator).'
            raise TypeError(reason)

        # Since the passed value is an iterator, we know all
        # TypeErrors will be caused by the contents of the
        # passed sequence.
        valid = tuple(self.validate(value) for value in seq)
        return valid

    @abstractmethod
    def validate(self, value):
        """Return the validated value or raise ValueError.

        :param value: The value to validate.
        :return: The canonicalized, normalized, validated value.
        :rtype: Varies.
        """


# Common validate functions.
def validate_bool(self, value):
    """Validate booleans."""
    if isinstance(value, bool):
        return value
    reason = 'not a bool'
    raise ValueError(self.msg.format(reason))


def validate_integer(self, value):
    """Normalize and validate integers."""
    if value is None:
        return 0
    try:
        return int(value)
    except ValueError:
        reason = 'cannot be made an integer'
        raise ValueError(self.msg.format(reason))


def validate_positive_int(self, value):
    """Validate integers that are positive numbers."""
    normal = validate_integer(self, value)
    if normal < 0:
        reason = 'cannot be less than 0'
        raise ValueError(self.msg.format(reason))
    return normal


def validate_text(self, value):
    """Normalize and validate text strings."""
    if isinstance(value, bytes):
        try:
            value = value.decode('utf_8')
        except UnicodeDecodeError:
            reason = 'contains invalid unicode characters'
            raise ValueError(self.msg.format(reason))
    try:
        canon = str(value)
    except (TypeError, ValueError):
        reason = 'cannot be made a string'
        raise ValueError(self.msg.format(reason))
    else:
        normal = normalize('NFC', canon)
        return normal


def validate_whitelist(self, value):
    """Validate items in a whitelist."""
    if value in self.whitelist:
        return value
    reason = 'not in list'
    raise ValueError(self.msg.format(reason))


def validate_yesno(self, value):
    """Validate yes/no responses from a UI."""
    if isinstance(value, bool):
        return value
    normal = value.lower()
    if normal == 'y' or normal == 'yes':
        return True
    if normal == 'n' or normal == 'no':
        return False
    reason = 'Not "yes" or "no".' + str(value)
    raise ValueError(self.msg.format(reason))


def valfactory(name, validator, message):
    """A factory for creating Validated subclasses."""
    attrs = {
        'validate': validator,
        'msg': message,
    }
    return type(name, (Validated,), attrs)


def valtupfactory(name, validator, message):
    """A factory for creating ValidatedTuple subclasses."""
    attrs = {
        'validate': validator,
        'msg': message,
    }
    return type(name, (ValidatedTuple,), attrs)


def wlistfactory(name:str, whitelist:Sequence, msg:str) -> type:
    """Create whitelist validators.

    :param name: The name of the validator.
    :param whitelist: The list of valid items.
    :param msg: The format string for the exceptions raised by the
        validator.
    :return: A validating descriptor for the whitelist.
    :rtype: type
    """
    attrs = {
        'validate': validate_whitelist,
        'msg': msg,
        'whitelist': whitelist,
    }
    return type(name, (Validated,), attrs)


# Common validating descriptors.
Boolean = valfactory('Boolean', validate_bool, 'Invalid bool({}).')
Integer_ = valfactory('Integer_', validate_integer, 'Invalid integer ({}).')
PosInt = valfactory('PosInt', validate_positive_int, 'Invalid ({}).')
Text = valfactory('PosInt', validate_text, 'Invalid text ({}).')
YesNo = valfactory('YesNo', validate_yesno, 'Invalid yes/no answer ({}).')

# Common sequence validating descriptors.
IntTuple = valtupfactory(
    'IntTuple',
    validate_text,
    'Invalid integer tuple ({}).'
)
TextTuple = valtupfactory(
    'TextTuple',
    validate_text,
    'Invalid text tuple ({}).'
)


# Common trusted objects.
class Bet:
    msg = 'Invalid ({}).'

    """User input that is a valid bet."""
    def __init__(
            self,
            value: str | int,
            value_max: Optional[int] = None,
            value_min: Optional[int] = None
    ):
        """Initialize and instance of the class.

        :param value: The bet.
        :return: None.
        :rtype: None.
        """
        self.value_max = value_max
        self.value_min = value_min

        # Setting this before the max and min will break the validation
        # built into the value property.
        self.value = validate_positive_int(self, value)

    def __eq__(self, other):
        cls = self.__class__
        if not isinstance(other, cls):
            return NotImplemented
        return self.value == other.value

    @property
    def value(self) -> int:
        """The value of the bet."""
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        """Setter and validation for the bet value."""
        if self.value_max is not None and value > self.value_max:
            reason = f'Invalid: value is greater than {self.value_max}.'
            raise ValueError(reason)
        if self.value_min is not None and value < self.value_min:
            reason = f'Invalid: value is less than {self.value_min}.'
            raise ValueError(reason)
        self._value = value


class IsYes:
    """User input that is either yes or no."""
    value = YesNo('value')

    def __init__(self, value: Union[str, bool]):
        """Initialize and instance of the class.

        :param value: Whether the answer was yes.
        :return: None.
        :rtype: None.
        """
        self.value = value

    def __eq__(self, other):
        cls = self.__class__
        if not isinstance(other, cls):
            return NotImplemented
        return self.value == other.value


# Base classes.
class EngineUI(ABC):
    # General operation methods.
    @abstractmethod
    def end(self):
        """End the UI."""

    @abstractmethod
    def reset(self):
        """Restart the UI."""

    @abstractmethod
    def start(self):
        """Start the UI."""

    # Input methods.
    @abstractmethod
    def bet_prompt(self, bet_min: int, bet_max: int) -> Bet:
        """Ask user for a bet.."""

    @abstractmethod
    def doubledown_prompt(self) -> IsYes:
        """Ask user if they want to double down."""

    @abstractmethod
    def hit_prompt(self) -> IsYes:
        """Ask user if they want to hit."""

    @abstractmethod
    def insure_prompt(self, insure_max: int) -> Bet:
        """Ask user if they want to insure."""

    @abstractmethod
    def nextgame_prompt(self) -> IsYes:
        """Ask user if they want to play another round."""

    @abstractmethod
    def split_prompt(self) -> IsYes:
        """Ask user if they want to split."""

    # Update methods.
    @abstractmethod
    def bet(self, player, bet):
        """Player places initial bet."""

    @abstractmethod
    def cleanup(self):
        """Clean up after the round ends."""

    @abstractmethod
    def deal(self, player, hand):
        """Player receives initial hand."""

    @abstractmethod
    def doubledown(self, player, bet):
        """Player doubles down."""

    @abstractmethod
    def flip(self, player, hand):
        """Player flips a card."""

    @abstractmethod
    def hit(self, player, hand):
        """Player hits."""

    @abstractmethod
    def insures(self, player, bet):
        """Player insures their hand."""

    @abstractmethod
    def insurepay(self, player, bet):
        """Insurance is paid to player."""

    @abstractmethod
    def joins(self, player):
        """Player joins the game."""

    @abstractmethod
    def leaves(self, player):
        """Player leaves the game."""

    @abstractmethod
    def loses(self, player):
        """Player loses."""

    @abstractmethod
    def loses_split(self, player):
        """Player loses on their split hand."""

    @abstractmethod
    def shuffles(self, player):
        """The deck is shuffled."""

    @abstractmethod
    def splits(self, player, bet):
        """Player splits their hand."""

    @abstractmethod
    def stand(self, player, hand):
        """Player stands."""

    @abstractmethod
    def tie(self, player, bet):
        """Player ties."""

    @abstractmethod
    def ties_split(self, player, bet):
        """Player ties on their split hand."""

    @abstractmethod
    def update_count(self, count):
        """Update the running card count in the UI."""

    @abstractmethod
    def wins(self, player, bet):
        """Player wins."""

    @abstractmethod
    def wins_split(self, player, bet):
        """Player wins on their split hand."""


class BaseEngine(ABC):
    bet_max: int
    bet_min: int
    card_count: int
    ui: EngineUI

    """The base class for the game engine."""
    @abstractmethod
    def bet(self) -> None:
        """Betting phase."""

    @abstractmethod
    def deal(self) -> None:
        """Dealing phase."""

    @abstractmethod
    def end(self) -> None:
        """End of the hand."""

    @abstractmethod
    def new_game(self) -> None:
        """Start a new game."""

    @abstractmethod
    def play(self) -> None:
        """Play the hand."""

    @abstractmethod
    def restore(self, fname: str) -> None:
        """Restore a game from a save."""

    @abstractmethod
    def save(self, fname: str) -> None:
        """Save a game."""

    @abstractmethod
    def serialize(self) -> None:
        """Serialize the game."""
