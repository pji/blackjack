"""
test_model.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.model module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import abc
import inspect
import unittest
from unittest.mock import call, Mock

from blackjack import model

class BaseDescriptorTests(unittest.TestCase):
    """Unit tests for model.BaseDescriptor."""
    def test_exists(self):
        """A class named _BaseDescriptor exists."""
        names = [item[0] for item in inspect.getmembers(model)]
        self.assertTrue('_BaseDescriptor' in names)
    
    def test_can_instantiate(self):
        """_BaseDescriptor can be instantiated."""
        descr = model._BaseDescriptor()
        self.assertTrue(isinstance(descr, model._BaseDescriptor))
    
    def test_is_descriptor(self):
        """_BaseDescriptor follows the descriptor protocol."""
        descr = model._BaseDescriptor()
        self.assertTrue(inspect.isdatadescriptor(descr))
    
    def test_creates_storage_name(self):
        """_BaseDescriptor objects use their hash to construct a 
        temporary storage name.
        """
        descr = model._BaseDescriptor()
        value = hash(descr)
        expected = f'__BaseDescriptor#{value}'
        
        actual = descr.storage_name
        
        self.assertEqual(expected, actual)
    
    def test_set_data(self):
        """_BaseDescriptor objects should set the value of the 
        protected attribute to the given value.
        """
        expected = 'spam'
        
        descr = model._BaseDescriptor()
        class Eggs:
            attr = descr
        obj = Eggs()
        obj.attr = expected
        actual = obj.__dict__[descr.storage_name]
        
        self.assertEqual(expected, actual)
    
    def test_get_data(self):
        """_BaseDescriptor objects should return the value of the 
        protected attribute.
        """
        expected = 'spam'
        
        descr = model._BaseDescriptor()
        class Eggs:
            attr = descr
        obj = Eggs()
        obj.__dict__[descr.storage_name] = expected
        actual = obj.attr
        
        self.assertEqual(expected, actual)
    
    def test_get_from_class(self):
        """_BaseDescriptor objects should return themselves when 
        the protected attribute is called on the protected attribute's 
        class.
        """
        expected = model._BaseDescriptor()
        
        class Eggs():
            attr = expected
        actual = Eggs.attr
        
        self.assertEqual(expected, actual)


class ValidatedTestCase(unittest.TestCase):
    def test_exists(self):
        """A class named Validated should exist."""
        names = [item[0] for item in inspect.getmembers(model)]
        self.assertTrue('Validated' in names)
    
    def test_ABC(self):
        """Validated should be an abstract base class."""
        self.assertTrue(issubclass(model.Validated, abc.ABC))
    
    def test_subclass_of__BaseDescriptor(self):
        """Validated should be a subclass of _BaseDescriptor."""
        self.assertTrue(issubclass(model.Validated, model._BaseDescriptor))
    
    def test_validator_required(self):
        """Subclasses of Validated should be required to define a 
        validate() method.
        """
        expected = TypeError
        
        class Spam(model.Validated):
            pass
        
        with self.assertRaises(expected):
            obj = Spam()
    
    def test_send_to_validator(self):
        """Validated subclasses should send data to their validator 
        method before setting it as the value of the protected 
        attribute.
        """
        s = 'spam'
        expected = call(s)
        
        class Descr(model.Validated):
            validate = Mock(return_value=expected)
        class Eggs:
            attr = Descr()
        obj = Eggs()
        obj.attr = s
        actual = Descr.validate.call_args
        
        self.assertEqual(expected, actual)
    
    def test_set_value(self):
        """Validated subclasses should set the value returned from 
        their validator method as the value of their protected 
        attribute.
        """
        expected = 'spam'
        
        class Descr(model.Validated):
            validate = Mock(return_value=expected)
        class Eggs:
            attr = Descr()
        obj = Eggs()
        obj.attr = expected
        actual = obj.attr
        
        self.assertEqual(expected, actual)
    
    def test_storage_name_initialization(self):
        """If passed the name of the protected attribute, instances of 
        subclasses of Validated should change their storage_name 
        attribute to be correctly mangled.
        """
        expected = '_Descr__attr'
        
        class Descr(model.Validated):
            validate = Mock()
        class Eggs:
            attr = Descr('attr')
        actual = Eggs.attr.storage_name
        
        self.assertEqual(expected, actual)
    

class valfactoryTestCase(unittest.TestCase):
    def test_exists(self):
        """A function named valfactory should exist."""
        names = [item[0] for item in inspect.getmembers(model)]
        self.assertTrue('valfactory' in names)
    
    def test_return_Validator_subclasses(self):
        """valfactory(), when given a name, a validator function, and 
        a message, should return subclasses of Validated.
        """
        expected = model.Validated
        
        name = 'Eggs'
        def validate(self, value):
            return value
        msg = 'Bad.'
        actual = model.valfactory(name, validate, msg)
        
        self.assertTrue(issubclass(actual, expected))
    
    def test_class_name(self):
        """The name of classes created by valfactory() should be the 
        name passed to valfactory.
        """
        expected = 'Spam'
        
        cls = model.valfactory(expected, Mock(), None)
        actual = cls.__name__
        
        self.assertEqual(expected, actual)
    
    def test_class_validator(self):
        """The validator for the class created by valfactory() should 
        be the validator passed to valfactory.
        """
        expected = Mock()
        
        cls = model.valfactory('Spam', expected, None)
        actual = cls.validate
        
        self.assertEqual(expected, actual)
    
    def test_class_message(self):
        """The value of the msg attribute for the class created by 
        valfactory should be the value of message passed to 
        valfactory().
        """
        expected = 'Bad.'
        
        cls = model.valfactory('Spam', Mock(), expected)
        actual = cls.msg
        
        self.assertEqual(expected, actual)


class validate_boolTestCase(unittest.TestCase):
    def test_exists(self):
        """A function named validate_bool should exist."""
        names = [item[0] for item in inspect.getmembers(model)]
        self.assertTrue('validate_bool' in names)
    
    def test_valid(self):
        """If passed a valid value, validate_bool should return it."""
        expected = True
        actual = model.validate_bool(None, expected)
        self.assertEqual(expected, actual)
    
    def test_invalid_type(self):
        """If passed a non-bool, validate_bool should reject it by 
        raising a ValueError.
        """
        expected = ValueError
        
        class Spam:
            msg = '{}'
        
        with self.assertRaises(expected):
            _ = model.validate_bool(Spam(), 'eggs')


class validate_integerTestCase(unittest.TestCase):
    def test_valid(self):
        """If passed a valid value, validate_integer should return it."""
        exp = [4, 3]
        values = [4, 3.0]
        act = [model.validate_integer(None, item) for item in exp]
        self.assertListEqual(exp, act)
    
    def test_invalid(self):
        """If passed an invalid value, validate_integer() should raise 
        a ValueError.
        """
        exp = ValueError
        
        class Spam:
            msg = '{}'
        test = 'eggs'
        
        with self.assertRaises(exp):
            _ = model.validate_integer(Spam(), test)


class validate__positive_intTestCase(unittest.TestCase):
    def test_valid(self):
        """If passed a valid value, validate_positive_ integer should 
        return it.
        """
        exp = [4, 3]
        values = [4, 3.0]
        act = [model.validate_positive_int(None, item) for item in exp]
        self.assertListEqual(exp, act)
    
    def test_invalid(self):
        """If passed an invalid value, validate_positive_int() should 
        raise a ValueError.
        """
        exp = ValueError
        
        class Spam:
            msg = '{}'
        test1 = -1
        test2 = 'spam'
        
        with self.assertRaises(exp):
            _ = model.validate_positive_int(Spam(), test1)

        with self.assertRaises(exp):
            _ = model.validate_positive_int(Spam(), test2)


class validate_textTestCase(unittest.TestCase):
    def test_valid(self):
        """If passed a valid value, validate_integer should return it."""
        exp = ['spam', '1']
        values = [b'spam', 1]
        act = [model.validate_text(None, item) for item in exp]
        self.assertListEqual(exp, act)
    
    def test_invalid(self):
        """If passed an invalid value, validate_integer() should raise 
        a ValueError.
        """
        exp = ValueError
        
        class Spam:
            msg = '{}'
        test = b'Montr\xe9al'
        
        with self.assertRaises(exp):
            _ = model.validate_integer(Spam(), test)


class validate_yesnoTestCase(unittest.TestCase):
    def test_valid_yes(self):
        """If passed a valid value, validate_yesno should return True 
        for values related to 'yes.'"""
        expected = True
        
        value1 = 'Y'
        value2 = 'y'
        value3 = 'Yes'
        value4 = True
        actual1 = model.validate_yesno(None, value1)
        actual2 = model.validate_yesno(None, value2)
        actual3 = model.validate_yesno(None, value3)
        actual4 = model.validate_yesno(None, value4)
        
        self.assertEqual(expected, actual1)
        self.assertEqual(expected, actual2)
        self.assertEqual(expected, actual3)
        self.assertEqual(expected, actual4)
    
    def test_valid_no(self):
        """If passed a valid value, validate_yesno should return True 
        for values related to 'yes.'"""
        expected = False
        
        value1 = 'n'
        value2 = 'N'
        value3 = 'No'
        value4 = False
        actual1 = model.validate_yesno(None, value1)
        actual2 = model.validate_yesno(None, value2)
        actual3 = model.validate_yesno(None, value3)
        actual4 = model.validate_yesno(None, value4)
        
        self.assertEqual(expected, actual1)
        self.assertEqual(expected, actual2)
        self.assertEqual(expected, actual3)
        self.assertEqual(expected, actual4)
    
    def test_invalid_value(self):
        """If passed an invalid value, validate_yesno should reject it 
        by raising a ValueError.
        """
        expected = ValueError
        
        class Spam:
            msg = '{}'
        
        with self.assertRaises(expected):
            _ = model.validate_yesno(Spam(), 'eggs')


# Common trusted object tests.
class YesNoTestCase(unittest.TestCase):
    def test_exists(self):
        """A function named validate_bool should exist."""
        names = [item[0] for item in inspect.getmembers(model)]
        self.assertTrue('IsYes' in names)