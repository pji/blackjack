"""
test_cli.py
~~~~~~~~~~~~~~~

This module contains the unit tests for the blackjack.cli module.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from contextlib import contextmanager
from io import StringIO
import sys
import unittest as ut

from blackjack import cards, cli, players


# Utility functions.
@contextmanager
def capture():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


# Tests.
class UITestCase(ut.TestCase):
    tmp = '{:<15} {:<15} {:<}\n'
    
    def test_initial_banners(self):
        """When a new UI object is initialized, it should print the 
        name of the application and the column headers to stdout.
        """
        lines = [
            '\n',
            'BLACKJACK!\n',
            '\n',
            self.tmp.format('Player', 'Action', 'Hand'),
            '\u2500' * 50 + '\n',
        ]
        expected = ''.join(lines)
        
        with capture() as (out, err):
            ui = cli.UI()
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_deal(self):
        """Given a message that cards have been dealt, the update() 
        method should print the result of the deal to stdout.
        """
        expected = self.tmp.format('Dealer', 'Initial deal.', '7♣ ──')
        
        ui = cli.UI(True)
        hand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(9, 2, cards.DOWN),
        ])
        with capture() as (out, err):
            ui.update('deal', 'Dealer', hand)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_play_hit(self):
        """Given a message a hit decision was made, the update() 
        method should print the result of the hit decision to stdout.
        """
        expected = self.tmp.format('Dealer', 'Hit.', '7♣ 6♣ 5♣')
        
        ui = cli.UI(True)
        hand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(6, 0, cards.UP),
            cards.Card(5, 0, cards.UP),
        ])
        with capture() as (out, err):
            ui.update('hit', 'Dealer', hand)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_play_stand(self):
        """Given an event that a stand decision was made, the update() 
        method should print the decision to stdout.
        """
        expected = self.tmp.format('Dealer', 'Stand.', '21')
        
        ui = cli.UI(True)
        event = 'stand'
        player = 'Dealer'
        hand = cards.Hand([
            cards.Card(11, 0, cards.UP),
            cards.Card(1, 1, cards.UP),
        ])
        with capture() as (out, err):
            ui.update(event, player, hand)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_play_stand_bust(self):
        """Given an event that a stand decision was made, the update() 
        method should print the decision to stdout.
        """
        expected = self.tmp.format('Dealer', 'Stand.', 'Bust.')
        
        ui = cli.UI(True)
        event = 'stand'
        player = 'Dealer'
        hand = cards.Hand([
            cards.Card(11, 0, cards.UP),
            cards.Card(7, 1, cards.UP),
            cards.Card(8, 1, cards.UP),
        ])
        with capture() as (out, err):
            ui.update(event, player, hand)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_play_flip(self):
        """Given an event that there was a card flipped, the update() 
        method should print the hand to stdout.
        """
        expected = self.tmp.format('Dealer', 'Flipped card.', '7♣ 6♣')
        
        ui = cli.UI(True)
        hand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(6, 0, cards.UP),
        ])
        with capture() as (out, err):
            ui.update('flip', 'Dealer', hand)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_play_split(self):
        """Given an event that a hand was split, the update() method 
        should print the new hands to stdout.
        """
        lines = [
            self.tmp.format('Terry', 'Hand split.', '7♣'),
            self.tmp.format('', '', '7♦'),
        ]
        expected = ''.join(lines)
        
        ui = cli.UI(True)
        player = players.AutoPlayer(name='Terry')
        hands = (
            cards.Hand([cards.Card(7, 0),]),
            cards.Hand([cards.Card(7, 1),]),
        )
        with capture() as (out, err):
            ui.update('split', player, hands)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_buyin(self):
        """Given an event that a player bought into the round, the 
        update() method should print the buyin to stdout.
        """
        bet = 20
        expected = self.tmp.format('John', 'Initial bet.', bet)
        
        ui = cli.UI(True)
        p1 = players.AutoPlayer(name='John', chips=bet)
#         g = game.Game(None, None, (p1,), ui, 20.00)
        with capture() as (out, err):
            ui.update('buyin', p1, bet)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_use_player_name(self):
        """If update() is given a player.Player object rather than 
        a string for the name field, update() should use the name 
        of that player.
        """
        expected = self.tmp.format('Dealer', 'Initial deal.', '7♣ ──')
        
        ui = cli.UI(True)
        player = players.Player(name='Dealer')
        hand = cards.Hand([
            cards.Card(7, 0, cards.UP),
            cards.Card(9, 2, cards.DOWN),
        ])
        with capture() as (out, err):
            ui.update('deal', player, hand)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_exit(self):
        """exit() should print the closing footers to stdout."""
        lines = [
            '\u2500' * 50 + '\n',
            '\n',
        ]
        expected = ''.join(lines)
        
        ui = cli.UI(True)
        with capture() as (out, err):
            ui.exit()
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)