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
from unittest.mock import patch, call

from blessed import Terminal

from blackjack import cards, cli, model, players


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
#             '\n',
#             self.tmp.format('Player', 'Action', 'Hand'),
#             '\u2500' * 50 + '\n',
        ]
        expected = ''.join(lines)
        
        with capture() as (out, err):
            ui = cli.UI()
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    
    # Test enter().
    def test_enter(self):
        """enter() should print the headers for the game output."""
        lines = [
#             '\n',
#             'BLACKJACK!\n',
            '\n',
            self.tmp.format('Player', 'Action', 'Hand'),
            '\u2500' * 50 + '\n',
        ]
        expected = ''.join(lines)
        
        with capture() as (out, err):
            ui = cli.UI(True)
            ui.enter()
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    
    # Test UI.update().
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
        fmt = '{} ({})'.format(bet, bet - bet)
        expected = self.tmp.format('John', 'Initial bet.', fmt)
        
        ui = cli.UI(True)
        p1 = players.AutoPlayer(name='John', chips=bet)
        with capture() as (out, err):
            ui.update('buyin', p1, [bet, bet - bet])
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_remove(self):
        """Given an event that a player was removed from the game, the 
        update() method should print the removal to stdout.
        """
        expected = self.tmp.format('Graham', 'Walks away.', '')
        
        ui = cli.UI(True)
        p1 = players.AutoPlayer(name='Graham')
        with capture() as (out, err):
            ui.update('remove', p1, None)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
        
    def test_update_end_wins(self):
        """Given an event that a player won, the 
        update() method should print victory to stdout.
        """
        fmt = '{} ({})'.format(40, 220)
        expected = self.tmp.format('Graham', 'Wins.', fmt)
        
        ui = cli.UI(True)
        p1 = players.AutoPlayer(name='Graham')
        with capture() as (out, err):
            ui.update('payout', p1, [40, 220])
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_end_tie(self):
        """Given an event that a player tied the dealer, the 
        update() method should print the tie to stdout.
        """
        fmt = '{} ({})'.format(20, 220)
        expected = self.tmp.format('Graham', 'Stand-off.', fmt)
        
        ui = cli.UI(True)
        p1 = players.AutoPlayer(name='Graham')
        with capture() as (out, err):
            ui.update('tie', p1, [20, 220])
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_doubled(self):
        """Given an event that a player doubled down on a hand, the 
        update() method should print the double down event to stdout.
        """
        fmt = '{} ({})'.format(40, 220)
        expected = self.tmp.format('Graham', 'Doubled down.', '40 (220)')
        
        ui = cli.UI(True)
        hand = cards.Hand([
            cards.Card(4, 3),
            cards.Card(7, 1),
        ])
        p1 = players.AutoPlayer((hand,), 'Graham', 220)
        with capture() as (out, err):
            ui.update('doubled', p1, [40, 220])
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_insured(self):
        """Given an event that a player bought insurance, the update() 
        method should print the insured event to stdout.
        """
        fmt = '{} ({})'.format(10, 220)
        expected = self.tmp.format('Graham', 'Insured.', fmt)
        
        ui = cli.UI(True)
        hand = cards.Hand([
            cards.Card(4, 3),
            cards.Card(7, 1),
        ])
        p1 = players.AutoPlayer((hand,), 'Graham', 220)
        with capture() as (out, err):
            ui.update('insured', p1, [10, 220])
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_insurepay(self):
        """Given an event that a player was payed out on insurance, 
        the update() method should print that event to stdout.
        """
        fmt = '{} ({})'.format(20, 220)
        expected = self.tmp.format('Graham', 'Insurance pay out.', fmt)
        
        ui = cli.UI(True)
        hand = cards.Hand([
            cards.Card(4, 3),
            cards.Card(7, 1),
        ])
        p1 = players.AutoPlayer((hand,), 'Graham', 220)
        with capture() as (out, err):
            ui.update('insurepay', p1, [20, 220])
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_shuffled(self):
        """Given an event that the game reshuffled the deck, the 
        update() method should print that event to stdout.
        """
        expected = self.tmp.format('Dealer', 'Shuffled deck.', '')
        
        ui = cli.UI(True)
        hand = cards.Hand([
            cards.Card(4, 3),
            cards.Card(7, 1),
        ])
        d = players.Dealer((hand,), 'Dealer', 220)
        with capture() as (out, err):
            ui.update('shuffled', d, None)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_join(self):
        """Given an event that a new player has joined the game, 
        the update() method should print that event to stdout.
        """
        expected = self.tmp.format('Graham', 'Walks up.', '')
        
        ui = cli.UI(True)
        d = players.AutoPlayer([], 'Graham', 220)
        with capture() as (out, err):
            ui.update('join', d, None)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_join_you(self):
        """Given an event that a new player has joined the game, 
        the update() method should print that event to stdout.
        """
        expected = self.tmp.format('You', 'Walk up.', '')
        
        ui = cli.UI(True)
        d = players.AutoPlayer([], 'You', 220)
        with capture() as (out, err):
            ui.update('join', d, None)
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
    
    
    # Test UI.input()
    @patch('blackjack.cli.input')
    def test_input_new_round(self, mock_input):
        """Given an event to prompt for a new game, the input() method 
        should prompt the user to see if they want to play a new game 
        and return the response.
        """
        mock_input.return_value = 'yes'
        expected_call = 'Another round? Y/n > '
        expected_return = model.IsYes(True)
        
        ui = cli.UI(True)
        actual_return = ui.input('nextgame')
        
        self.assertEqual(expected_return.value, actual_return.value)
        mock_input.assert_called_with(expected_call)
    
    @patch('blackjack.cli.input')
    def test_input_hit(self, mock_input):
        """Given a prompt to hit, the input() method should prompt the 
        user to see if they want to hit and return the response.
        """
        mock_input.return_value = 'yes'
        expected_call = 'Hit? Y/n > '
        expected_return = model.IsYes(True)
        
        ui = cli.UI(True)
        actual_return = ui.input('hit')
        
        self.assertEqual(expected_return.value, actual_return.value)
        mock_input.assert_called_with(expected_call)
    
    @patch('blackjack.cli.input')
    def test_input_split(self, mock_input):
        """Given a prompt to split, the input() method should prompt the 
        user to see if they want to split and return the response.
        """
        mock_input.return_value = 'yes'
        expected_call = 'Split? Y/n > '
        expected_return = model.IsYes(True)
        
        ui = cli.UI(True)
        actual_return = ui.input('split')
        
        self.assertEqual(expected_return.value, actual_return.value)
        mock_input.assert_called_with(expected_call)
    
    @patch('blackjack.cli.input')
    def test_input_double_down(self, mock_input):
        """Given a prompt to hit, the input() method should prompt the 
        user to see if they want to hit and return the response.
        """
        mock_input.return_value = 'yes'
        expected_call = 'Double down? Y/n > '
        expected_return = model.IsYes(True)
        
        ui = cli.UI(True)
        actual_return = ui.input('doubledown')
        
        self.assertEqual(expected_return.value, actual_return.value)
        mock_input.assert_called_with(expected_call)
    
    @patch('blackjack.cli.input')
    def test_input_insure(self, mock_input):
        """Given a prompt to insure, the input() method should prompt 
        the user to see if they want to hit and return the response.
        """
        mock_input.return_value = 'yes'
        expected_call = 'Insure? Y/n > '
        expected_return = model.IsYes(True)
        
        ui = cli.UI(True)
        actual_return = ui.input('insure')
        
        self.assertEqual(expected_return.value, actual_return.value)
        mock_input.assert_called_with(expected_call)
    
    
    # Test UI.exit().
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


class DynamicUITestCase(ut.TestCase):
    def test_init(self):
        """A DynamicUI object should initialize the following 
        attributes: rows, tmp.
        """
        exp_rows = []
        
        ui = cli.DynamicUI()
        act_rows = ui.rows
        
        self.assertEqual(exp_rows, act_rows)
    
    # Test DynamicUI.update().
    @patch('blackjack.cli.run_terminal')
    def test_update_join(self, mock_term):
        """Given an event that a new player has joined the game, 
        the update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 220)
        expected = call().send(('join', player))
        
        ui = cli.DynamicUI()
        ui.update('join', player, '')
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_deal(self, mock_term):
        """Given an event that a player has bet, the update() method 
        should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 220)
        hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 0),
        ])
        expected = call().send(('deal', player, hand))
        
        ui = cli.DynamicUI()
        ui.update('deal', player, hand)
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_buyin(self, mock_term):
        """Given an event that a player has bet, the update() method 
        should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 220)
        expected = call().send(('buyin', player, 20))
        
        ui = cli.DynamicUI()
        ui.update('buyin', player, [20, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)



class run_terminalTestCase(ut.TestCase):
    bold = '\x1b[1m'
    ascii = '\x1b(B'
    default = '\x1b[m'
    h_tmp = '{:<14} {:>7} {:>3} {:<27} {:<}'
    r_tmp = '{:<14} {:>7} {:>3} {:<27} {:<}'
    
    def test_init(self):
        """When sent an init message, run_terminal() should display 
        the game screen with headers, footers, and enough space for 
        player seats.
        """
        headers = ('Player', 'Chips', 'Bet', 'Hand', 'Event')
        lines = [
            f'{self.bold}BLACKJACK{self.ascii}{self.default}\n',
            f'\n' + self.h_tmp.format(*headers) + '\n',
            '\u2500' * 80 + '\n',
            '\n',
            '\n',
            '\u2500' * 80 + '\n',
        ]
        expected = ''.join(lines)
        
        seats = 2
        with capture() as (out, err):
            term = cli.run_terminal()
            next(term)
            term.send(('init', 2))
        actual = out.getvalue()
        del term
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_join(self, mock_print):
        """When sent a join message, run_terminal() should display 
        the player's name, chips, and a join message in the first 
        open row.
        """
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        values = [[p.name, p.chips, '', '', 'Joins game.'] for p in playerlist]
        expected = [
            call('\x1b[5;1H' + self.r_tmp.format(*values[0])),
            call('\x1b[6;1H' + self.r_tmp.format(*values[1])),
        ]
        
        term = cli.run_terminal()
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        actual = mock_print.mock_calls[-2:]
        del term

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_buyin(self, mock_print):
        """When sent a buyin message, run_terminal() should display
        the player's bet in the player's row and show their new chips 
        total.
        """
        expected = [
            call('\x1b[5;16H' + '    200' + '\x1b[5;24H' + ' 20'),
            call('\x1b[6;16H' + '    200' + '\x1b[6;24H' + ' 20'),
        ]
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        
        term = cli.run_terminal()
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('buyin', playerlist[0], 20))
        term.send(('buyin', playerlist[1], 20))
        actual = mock_print.mock_calls[-2:]
        del term

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_deal(self, mock_print):
        """When sent a deal message, run_terminal() should display
        the player's hand in the player's row.
        """
        expected = [
            call('\x1b[5;28H' + 'J♣ A♦'),
            call('\x1b[6;28H' + 'J♠ A♥'),
        ]
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        hand0 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(1, 1),
        ])
        hand1 = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 2),
        ])
        term = cli.run_terminal()
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('buyin', playerlist[0], 20))
        term.send(('buyin', playerlist[1], 20))
        term.send(('deal', playerlist[0], hand0))
        term.send(('deal', playerlist[1], hand1))
        actual = mock_print.mock_calls[-2:]
        del term

        self.assertEqual(expected, actual)

