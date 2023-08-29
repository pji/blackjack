"""
test_model.py
~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.model module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from functools import partial

import pytest

from blackjack import model


# Utility functions.
def raises_test(cls, *args, **kwargs):
    """Return the exception raised by the callable."""
    try:
        cls(*args, **kwargs)
    except Exception as ex:
        return type(ex), str(ex)
    return None


def validator_test(fn, self, value):
    try:
        return fn(self, value)
    except Exception as ex:
        return type(ex), str(ex)


# Tests for ABCs.
def test__BaseDescriptor():
    """:class:`_BaseDescriptor` should protect its assigned attribute."""
    descr = model._BaseDescriptor()

    class Spam:
        attr = descr

    obj = Spam()
    obj.attr = 'eggs'
    assert obj.attr == 'eggs'
    assert 'attr' not in obj.__dict__
    assert obj.__dict__[descr.storage_name] == 'eggs'
    assert vars(Spam)['attr'] == descr


def test_Validated(mocker):
    """:class:`Validated` subclasses should send data to their
    :meth:`Validator.validator` method before setting it as the
    value of the protected attribute.
    """
    class Descr(model.Validated):
        validate = mocker.Mock(return_value='spam')

    class Eggs:
        attr = Descr('attr')

    obj = Eggs()
    obj.attr = 'spam'
    assert obj.attr == 'spam'
    assert obj.__dict__['_Descr__attr'] == 'spam'
    assert Descr.validate.mock_calls == [
        mocker.call('spam'),
    ]


def test_ValidatedTuple():
    """If passed a non-iterator, subclasses of :class:`ValidatedTuple`
    should raise a :class:`TypeError`. If passed an iterator, the
    contents of the iterator should be stored as a :class:`tuple`.
    """
    class Descr(model.ValidatedTuple):
        def validate(self, value):
            return value

    class Spam:
        attr = Descr('attr')

    obj = Spam()
    obj.attr = [1, 2, 3]
    assert obj.attr == (1, 2, 3)
    assert obj.__dict__['_Descr__attr'] == (1, 2, 3)
    with pytest.raises(TypeError):
        obj.attr = 6


# Tests for factories.
def test_valfactory():
    """Given a name, a validator function, and a message,
    :func:`valfactory` should return a validating descriptor
    that uses the given validator function to validate data.
    """
    def validate(self, value):
        if value == 'spam':
            return 'spam'
        raise ValueError(self.msg)

    Spam = model.valfactory('Spam', validate, 'Not spam.')

    class Eggs:
        attr = Spam('attr')

    obj = Eggs()
    obj.attr = 'spam'
    assert obj.attr == 'spam'
    assert obj.__dict__['_Spam__attr'] == 'spam'
    with pytest.raises(ValueError, match='Not spam[.]'):
        obj.attr = 6


def test_valtupfactory():
    """Given a name, a validator function, and a message,
    :func:`valtupfactory` should return a validating descriptor
    that uses the given validator function to validate data
    returned from the iterator.
    """
    def validate(self, value):
        if value == 'spam':
            return 'spam'
        raise ValueError(self.msg)

    Spam = model.valtupfactory('Spam', validate, 'Not spam.')

    class Eggs:
        attr = Spam('attr')

    obj = Eggs()
    obj.attr = ['spam', 'spam', 'spam',]
    assert obj.attr == ('spam', 'spam', 'spam',)
    assert obj.__dict__['_Spam__attr'] == ('spam', 'spam', 'spam',)
    with pytest.raises(ValueError, match='Not spam[.]'):
        obj.attr = 'spam'


def test_wlistfactory():
    """Given a name, a list of valid values, and a message,
    :func:`valfactory` should return a validating descriptor
    that only allows values in the given list of valid values.
    """
    Spam = model.wlistfactory('Spam', ['spam', 'eggs'], 'Not spam.')

    class Bacon:
        attr = Spam('attr')

    obj = Bacon()
    obj.attr = 'spam'
    assert obj.attr == 'spam'
    assert obj.__dict__['_Spam__attr'] == 'spam'
    with pytest.raises(ValueError, match='Not spam[.]'):
        obj.attr = 6


# Fixtures for validator functions.
@pytest.fixture
def msgobj(request):
    class Spam:
        msg = '{}'
    return Spam()


# Tests for validator functions.
def test_validate_bool(msgobj):
    """:func:`validate_bool` should accept :class:`bool` or bool-like
    values.
    """
    accepts = partial(validator_test, model.validate_bool, msgobj)
    assert accepts(True) is True
    assert accepts(False) is False
    assert accepts(6) == (ValueError, 'not a bool')
    assert accepts('spam') == (ValueError, 'not a bool')


def test_validate_integer(msgobj):
    """:func:`validate_integer` should accept :class:`int` or int-like
    values.
    """
    accepts = partial(validator_test, model.validate_integer, msgobj)
    assert accepts(3) == 3
    assert accepts(-3) == -3
    assert accepts(None) == 0
    assert accepts(3.0) == 3
    assert accepts('3') == 3
    assert accepts('spam') == (ValueError, 'cannot be made an integer')


def test_validate_positive_int(msgobj):
    """:func:`validate_positive_int` should accept :class:`int` or
    int-like values.
    """
    accepts = partial(validator_test, model.validate_positive_int, msgobj)
    assert accepts(3) == 3
    assert accepts(None) == 0
    assert accepts(3.0) == 3
    assert accepts('3') == 3
    assert accepts(-3) == (ValueError, 'cannot be less than 0')
    assert accepts('spam') == (ValueError, 'cannot be made an integer')


def test_validate_text(msgobj):
    """:func:`validate_text` should accept :class:`str` or
    str-like values.
    """
    accepts = partial(validator_test, model.validate_text, msgobj)
    assert accepts('spam') == 'spam'
    assert accepts(b'spam') == 'spam'
    assert accepts('') == ''
    assert accepts(3) == '3'
    assert accepts(b'Montr\xe9al') == (
        ValueError,
        'contains invalid unicode characters'
    )


def test_validate_whitelist(msgobj):
    """:func:`validate_whitelist` should accept members of a given list
    of values.
    """
    accepts = partial(validator_test, model.validate_whitelist, msgobj)
    msgobj.whitelist = ['spam', 'eggs']
    assert accepts('spam') == 'spam'
    assert accepts('eggs') == 'eggs'
    assert accepts('ham') == (ValueError, 'not in list')
    assert accepts(3) == (ValueError, 'not in list')


def test_validate_yesno(msgobj):
    """:func:`validate_yesno` should accept 'yes', 'no', or
    :class:`bool`.
    """
    accepts = partial(validator_test, model.validate_yesno, msgobj)
    assert accepts('Y')
    assert accepts('y')
    assert accepts('Yes')
    assert accepts(True)
    assert accepts('N') is False
    assert accepts('n') is False
    assert accepts('No') is False
    assert accepts(False) is False
    assert accepts('spam') == (ValueError, 'Not "yes" or "no".')
    assert accepts(None) == (TypeError, 'Not bool or str.')


# Common trusted object tests.
def test_Bet_init_default():
    """Given only required values, the :class:`Bet` object's required
    attributes should be set to the given values, and the :class:`Bet`
    object's optional attributes should be set to default values.
    """
    requireds = {'value': 200,}
    optionals = {
        'value_max': None,
        'value_min': None,
    }
    obj = model.Bet(**requireds)
    for attr in requireds:
        assert getattr(obj, attr) == requireds[attr]
    for attr in optionals:
        assert getattr(obj, attr) == optionals[attr]


def test_Bet_init_invalid():
    """Given invalid values, :class:`Bet` should raise the appropriate
    exception.
    """
    raises = partial(raises_test, model.Bet)
    assert raises(3, value_max=2, value_min=1) == (
        ValueError,
        'Invalid: value is greater than 2.'
    )
    assert raises(0, value_max=2, value_min=1) == (
        ValueError,
        'Invalid: value is less than 1.'
    )
    assert raises('spam', value_max=2, value_min=1) == (
        ValueError,
        'Invalid (cannot be made an integer).'
    )


def test_Bet_init_optional():
    """Given values, the :class:`Bet` object's attributes should be set
    to the given values.
    """
    requireds = {'value': 200,}
    optionals = {
        'value_max': 500,
        'value_min': 20,
    }
    obj = model.Bet(**requireds, **optionals)
    for attr in requireds:
        assert getattr(obj, attr) == requireds[attr]
    for attr in optionals:
        assert getattr(obj, attr) == optionals[attr]


def test_IsYes_init_default():
    """Given required values, the :class:`IsYes` object's required
    attributes should be set to the given values. :class:`IsYes` has
    no optional attributes.
    """
    requireds = {'value': True,}
    obj = model.IsYes(**requireds)
    for attr in requireds:
        assert getattr(obj, attr) == requireds[attr]


def test_IsYes_init_invalid():
    """Given invalid values, :class:`IsYes` should raise the appropriate
    exception.
    """
    raises = partial(raises_test, model.IsYes)
    assert raises(None) == (TypeError, 'Not bool or str.')
    assert raises('spam') == (
        ValueError,
        'Invalid yes/no answer (Not "yes" or "no".).'
    )
