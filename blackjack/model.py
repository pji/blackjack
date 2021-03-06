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
from typing import Any, Iterable, Sequence

class _BaseDescriptor:
    """A basic data descriptor."""
    
    def __init__(self):
        cls = self.__class__
        self_hash = hash(self)
        self.storage_name = f'_{cls.__name__}#{self_hash}'
    
    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)
    
    def __get__(self, instance, owner):
        if instance != None:
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
    if value == None:
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
IntTuple = valtupfactory('IntTuple', validate_text, 'Invalid integer tuple ({}).')
TextTuple = valtupfactory('TextTuple', validate_text, 'Invalid text tuple ({}).')


# Common trusted objects.
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