"""
model
~~~~~

The module contains the basic classes used to build blackjack's 
data model.
"""
from abc import ABC, abstractmethod

class _BaseDescriptor:
    """A basic data descriptor."""
    
    def __init__(self):
        cls = self.__class__
        self_hash = hash(self)
        self.storage_name = f'_{cls.__name__}#{self_hash}'
    
    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)
    
    def __get__(self, instance, owner):
        if instance:
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


def valfactory(name, validator, message):
    """A factor for creating Validator subclasses."""
    attrs = {
        'validate': validator,
        'msg': message,
    }
    return type(name, (Validated,), attrs)