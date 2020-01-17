"""
test_termui.py
~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.termui module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import unittest as ut

from blessed import Terminal

from blackjack import termui


class BoxTestCase(ut.TestCase):
    def test_normal(self):
        "A Box object should return box characters."""
        expected = {
            'top': '\u2500',
            'bot': '\u2500',
            'side': '\u2502',
            'ltop': '\u250c',
            'rtop': '\u2510',
            'mtop': '\u252c',
            'lbot': '\u2514',
            'rbot': '\u2518',
            'mbot': '\u2534',
            'lside': '\u251c',
            'rside': '\u2524',
            'mid': '\u253c',
        }
        
        box = termui.Box()
        for attr in expected:
            actual = getattr(box, attr)
            
            self.assertEqual(expected[attr], actual)
    
    def test_change_type(self):
        """If given a kind, the kind property should change the kind 
        attribute and the _chars attribute.
        """
        expected = ['\u2500', '\u2501', '\u2508']
        
        box = termui.Box('light')
        actual = [box.top,]
        box.kind = 'heavy'
        actual.append(box.top)
        box.kind = 'light_quadruple_dash'
        actual.append(box.top)
        
        self.assertEqual(expected, actual)
    
    def test_custom(self):
        """If given a kind of 'custom' string of characters, the box
         object should return the custom characters and it's kind 
         should be 'custom'.
        """
        exp_kind = 'custom'
        exp_chars = 'abcdefghijklmn'
        exp_sample = 'g'
        
        box = termui.Box(custom=exp_chars)
        act_kind = box.kind
        act_chars = box._chars
        act_sample = box.mtop
        
        self.assertEqual(exp_kind, act_kind)
        self.assertEqual(exp_chars, act_chars)
        self.assertEqual(exp_sample, act_sample)
    
    def test_invalid_custom_string(self):
        """The passed custom string is not exactly fourteen characters 
        long, a ValueError should be raised.
        """
        expected = ValueError
        
        with self.assertRaises(expected):
            box = termui.Box(custom='bad')


class TableTestCase(ut.TestCase):
    def test_init_attributes(self):
        """When initialized, Table should accept values for the 
        class's required attributes.
        """
        fields = [
            ('Eggs', 0, '{}', None),
            ('Baked Beands', 40, '{}', None)
        ]
        expected = {
            'title': 'Spam',
            'fields': [termui.Field(*args) for args in fields]
        }
        
        obj = termui.Table(**expected)
        for attr in expected:
            actual = getattr(obj, attr)
            
            self.assertEqual(expected[attr], actual)
    
    def test_init_no_data(self):
        """When initialized, if data is not passed, an initial empty 
        table should be built.
        """
        expected = []
        
        fields = [
            ('Eggs', 0, '{}', None),
            ('Baked Beands', 40, '{}', None)
        ]
        attrs = {
            'title': 'Spam',
            'fields': [termui.Field(*args) for args in fields]
        }
        obj = termui.Table(**attrs)
        actual = obj.data
            
        self.assertEqual(expected, actual)

    def test_init_optional_attrs(self):
        """When initialized, Table should accept values for the 
        class's optional attributes.
        """
        fields = [
            ('Eggs', 0, '{}', None),
            ('Baked Beands', 40, '{}', None)
        ]
        data = [
            [1, 2, 3],
            [4, 5, 6],
        ]
        expected = {
            'title': 'Spam',
            'fields': [termui.Field(*args) for args in fields],
            'frame': termui.Box('light'),
            'data': data,
            'term': Terminal()
        }
        
        obj = termui.Table(**expected)
        for attr in expected:
            actual = getattr(obj, attr)
            
            self.assertEqual(expected[attr], actual)


class mainTestCase(ut.TestCase):
    def test_init_with_params(self):
        """main() should create its own instances of term and ctlr if 
        none are supplied.
        """
        ctlr = termui.TerminalController()
        main = termui.main(ctlr)
        
        # This will fail the test due to a exception if 
        # ctlr.term.fullscreen cannot be called.
        next(main)
    
    def test_init_no_params(self):
        """main() should create its own TerminalController if one is 
        not passed.
        """
        main = termui.main()
        
        # This will fail the test due to a exception if 
        # ctlr.term.fullscreen cannot be called.
        next(main)