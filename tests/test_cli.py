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
from unittest.mock import patch, call, MagicMock

from blessed import Terminal

from blackjack import cards, cli, game, model, players, termui


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


def mock_run_terminal_only_yesno():
    values = [None, model.IsYes(True)]
    for value in values:
        yield value


# Tests.
class TableUITestCase(ut.TestCase):
    def test_subclass(self):
        """TableUI is a subclass of game.EngineUI."""
        exp = game.EngineUI
        act = cli.TableUI
        self.assertTrue(issubclass(act, exp))
    
    # General operations methods.
    def test_init_optional_attrs(self):
        """On initialization, TableUI should accept optional 
        attributes.
        """
        fields = [
            ['Name', '{:<10}',],
            ['Value', '{:<10}',],
        ]
        ctlr = termui.Table('spam', fields)
        exp = {
            'ctlr': ctlr,
            'seats': 6,
        }
        
        ui = cli.TableUI(**exp)
        for attr in exp:
            act = getattr(ui, attr)
            
            self.assertEqual(exp[attr], act)
    
    def test_init_no_optional_attrs(self):
        """On initialization, TableUI should not require optional 
        attributes.
        """
        exp = termui.Table
        
        ui = cli.TableUI()
        act = ui.ctlr
        
        self.assertTrue(isinstance(act, exp))
    
    @patch('blackjack.termui.main')
    def test_start(self, mock_main):
        """start() should kick off the main loop of the UI, set it 
        as the loop attribute, and prime it.
        """
        ui = cli.TableUI()
        term = ui.ctlr
        exp = [
            call(ui.ctlr, False),
            call().__next__(),
            call().send(('draw',))
        ]
        
        ui.start()
        act = mock_main.mock_calls
        
        self.assertEqual(exp, act)
    
    @patch('blackjack.termui.main')
    def test_end(self, mock_main):
        """end() should terminate UI loop gracefully."""
        exp = call().close()
        
        ui = cli.TableUI()
        ui.start()
        ui.end()
        act = mock_main.mock_calls[-1]
        
        self.assertEqual(exp, act)
    
    
    # Update method tests.
    @patch('blackjack.termui.main')
    def test__update_bet(self, mock_main):
        """_update_bet should send an event to the UI loop that a 
        player's bet has changed and needs to be updated. The data 
        sent in that event should be a copy of the table in the 
        termui.Table object. 
        """
        player = players.Player(name='spam', chips=80)
        msg = 'Bets.'
        new_data = [[player, 80, 20, '', msg],]
        exp = call().send(('update', new_data))
        
        unexp_data = [[player, 100, '', '', ''],]
        ui = cli.TableUI()
        ui.ctlr.data = unexp_data
        ui.start()
        ui._update_bet(player, 20, msg)
        act = mock_main.mock_calls[-1]
        ui.end()
        
        self.assertEqual(exp, act)
        
        # Since termui.Table determines what fields to update based 
        # on differences between it's data table and the data table 
        # it's sent, it's very important that the changes made to 
        # the data table output by _update_bet() are not yet seen in 
        # the data table held by termui.Table.
        #
        # If this test fails, it's likely because you aren't copying 
        # the rows of self.ctrl.data. You are referencing them.
        self.assertNotEqual(unexp_data[0][1], 80)
    
    @patch('blackjack.termui.main')
    def test__update_event(self, mock_main):
        """_update_event should send an event to the UI loop that a 
        player has had an event occur. The data sent in that event 
        should be a copy of the table in the termui.Table object. 
        """
        player = players.Player(name='spam', chips=80)
        msg = 'Walks away.'
        new_data = [[player, 80, '', '', msg],]
        exp = call().send(('update', new_data))
        
        unexp_data = [[player, 80, '', '', ''],]
        ui = cli.TableUI()
        ui.ctlr.data = unexp_data
        ui.start()
        ui._update_event(player, msg)
        act = mock_main.mock_calls[-1]
        ui.end()
        
        self.assertEqual(exp, act)
        
        # Since termui.Table determines what fields to update based 
        # on differences between it's data table and the data table 
        # it's sent, it's very important that the changes made to 
        # the data table output by _update_bet() are not yet seen in 
        # the data table held by termui.Table.
        #
        # If this test fails, it's likely because you aren't copying 
        # the rows of self.ctrl.data. You are referencing them.
        self.assertNotEqual(unexp_data[0][4], 'Takes hand.')
    
    @patch('blackjack.termui.main')
    def test__update_hand(self, mock_main):
        """_update_bet should send an event to the UI loop that a 
        player's hand has changed and needs to be updated. The data 
        sent in that event should be a copy of the table in the 
        termui.Table object. 
        """
        hand = cards.Hand((
            cards.Card(11, 0),
            cards.Card(5, 2),
        ))
        player = players.Player(name='spam', chips=80)
        msg = 'Takes hand.'
        new_data = [[player, 80, 20, str(hand), msg],]
        exp = call().send(('update', new_data))
        
        unexp_data = [[player, 80, 20, '', 'Bets.'],]
        ui = cli.TableUI()
        ui.ctlr.data = unexp_data
        ui.start()
        ui._update_hand(player, hand, msg)
        act = mock_main.mock_calls[-1]
        ui.end()
        
        self.assertEqual(exp, act)
        
        # Since termui.Table determines what fields to update based 
        # on differences between it's data table and the data table 
        # it's sent, it's very important that the changes made to 
        # the data table output by _update_bet() are not yet seen in 
        # the data table held by termui.Table.
        #
        # If this test fails, it's likely because you aren't copying 
        # the rows of self.ctrl.data. You are referencing them.
        self.assertNotEqual(unexp_data[0][4], 'Takes hand.')
        
    @patch('blackjack.termui.print')
    @patch('blackjack.cli.TableUI._update_bet')
    def test_bet_updates(self, mock_update_bet, _):
        """The tested methods should call the _update_bet() method 
        with the player, bet, and event text.
        """
        player = players.Player(name='spam', chips=100)
        bet = 20
        exp = [
            call(player, bet, 'Bets.'),
            call(player, bet, 'Doubles down.'),
            call(player, bet, f'Buys {bet} insurance.'),
            call(player, bet, f'Insurance pays {bet}.'),
            call(player, '', 'Loses.'),
            call(player, '', 'Loses.', True),
            call(player, '', f'Ties {bet}.'),
            call(player, '', f'Wins {bet}.'),
            call(player, '', f'Ties {bet}.', True),
            call(player, '', f'Wins {bet}.', True),
        ]
        
        data = [[player, 80, 20, '', ''],]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.bet(player, bet)
        ui.doubledown(player, bet)
        ui.insures(player, bet)
        ui.insurepay(player, bet)
        ui.loses(player)
        ui.loses_split(player)
        ui.tie(player, bet)
        ui.wins(player, bet)
        ui.ties_split(player, bet)
        ui.wins_split(player, bet)
        act = mock_update_bet.mock_calls[-10:]
        ui.end()
        
        self.assertEqual(exp, act)
    
    @patch('blackjack.termui.print')
    @patch('blackjack.cli.TableUI._update_event')
    def test_event_updates(self, mock_update_event, _):
        """The tested methods should call the _update_event() method 
        with the player and event text.
        """
        player = players.Player(name='spam', chips=100)
        exp = [
            call(player, 'Shuffles the deck.'),
        ]
        
        data = [[player, 80, 20, '', ''],]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.shuffles(player)
        act = mock_update_event.mock_calls[-1:]
        ui.end()
        
        self.assertEqual(exp, act)
    
    @patch('blackjack.termui.print')
    @patch('blackjack.cli.TableUI._update_hand')
    def test_hand_updates(self, mock_update_hand, _):
        """The tested methods should call the _update_hand() method 
        with the player, hand, and event text.
        """
        player = players.Player(name='spam', chips=100)
        hand = cards.Hand([
            cards.Card(11, 0),
            cards.Card(10, 3),
        ])
        handstr = str(hand)
        exp = [
            call(player, hand, 'Takes hand.'),
            call(player, hand, 'Flips card.'),
            call(player, hand, 'Hits.'),
            call(player, hand, 'Stands.'),
        ]
        
        data = [[player, 80, 20, '', ''],]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.deal(player, hand)
        ui.flip(player, hand)
        ui.hit(player, hand)
        ui.stand(player, hand)
        act = mock_update_hand.mock_calls[-4:]
        ui.end()
        
        self.assertEqual(exp, act)
    
    @patch('blackjack.termui.main')
    def test_splits(self, mock_main):
        """When given a player and a bet, splits() should add a row 
        to the data table for the split hand, update it with the 
        relevant information, and send it to the UI.
        """
        hands = [
            cards.Hand([cards.Card(11, 0),]),
            cards.Hand([cards.Card(11, 3),]),
        ]
        player = players.Player(hands, name='spam', chips=100)
        player2 = players.Player(hands, name='eggs', chips=100)
        new_data = [
            [player, 100, 20, 'J♣', 'Splits hand.'], 
            ['  \u2514\u2500', '', 20, 'J♠', ''],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'], 
        ]
        exp_call = call().send(('update', new_data))
        unexp_len = len(new_data)
        
        data = [
            [player, 100, 20, 'J♣ J♠', 'Takes hand.'], 
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'], 
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.splits(player, 20)
        act_call = mock_main.mock_calls[-1]
        act_len = len(data)
        ui.end()
        
        self.assertEqual(exp_call, act_call)
        self.assertNotEqual(unexp_len, act_len)
    
    @patch('blackjack.termui.main')
    def test_leaves(self, mock_main):
        """When given a player, leaves() should announce the player is 
        leaving and remove the player from the data table. In order to 
        avoid the row in the UI just going blank, this call will edit 
        self.ctlr.data directly.
        """
        player = players.Player(name='spam', chips=100)
        player2 = players.Player(name='eggs', chips=100)
        new_data = [
            [player, '', '', '', 'Walks away.'],
            [player2, 100, '', '', 'Sits down.'], 
        ]
        exp_call = call().send(('update', new_data))
        exp_data = [
            ['', '', '', '', 'Walks away.'],
            [player2, 100, '', '', 'Sits down.'], 
        ]
        
        data = [
            [player, 100, '', '', 'Sits down.'],
            [player2, 100, '', '', 'Sits down.'], 
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        def update_data(ctlr, data):
            ctlr.data = data
        mock_main.side_effect= update_data(ui.ctlr, [r[:] for r in new_data])
        ui.start()
        ui.leaves(player)
        act_call = mock_main.mock_calls[-1]
        act_data = ui.ctlr.data
        ui.end()
        
        self.assertEqual(exp_call, act_call)
        self.assertEqual(exp_data, act_data)
    
    @patch('blackjack.termui.main')
    def test_joins(self, mock_main):
        """When given a player, joins() should add the player to the 
        data table in the first empty row.
        """
        player = players.Player(name='spam', chips=100)
        player2 = players.Player(name='eggs', chips=100)
        new_data1 = [
            [player, 100, '', '', 'Sits down.'], 
            ['', '', '', '', ''],
        ]
        new_data2 = [
            [player, 100, '', '', 'Sits down.'], 
            [player2, 100, '', '', 'Sits down.'], 
        ]
        exp_call = [
            call().send(('update', new_data1)),
            call().send(('update', new_data2)),
        ]
        
        data = [
            ['', '', '', '', ''],
            ['', '', '', '', ''],
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.joins(player)
        ui.ctlr.data = new_data1
        ui.joins(player2)
        act_call = mock_main.mock_calls[-2:]
        ui.end()
        
        self.assertEqual(exp_call, act_call)
        self.assertNotEqual(new_data2, new_data1)
    
    @patch('blackjack.termui.main')
    def test__update_bet_split(self, mock_main):
        """When is_split is True, _update_bet should update the split 
        row of the data table for the player.
        """
        hands = [
            cards.Hand([cards.Card(11, 0),]),
            cards.Hand([cards.Card(11, 3),]),
        ]
        player = players.Player(hands, name='spam', chips=100)
        player2 = players.Player(name='eggs', chips=100)
        new_data = [
            [player, 100, 20, 'J♣', 'Splits hand.'], 
            ['  \u2514\u2500', '', 20, 'J♠', 'Loses.'],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'], 
        ]
        exp = call().send(('update', new_data))
        
        data = [
            [player, 100, 20, 'J♣', 'Splits hand.'], 
            ['  \u2514\u2500', '', '', 'J♠', ''],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'], 
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui._update_bet(player, 20, 'Loses.', split=True)
        act = mock_main.mock_calls[-1]
        ui.end()
        
        self.assertEqual(exp, act)
    
    @patch('blackjack.termui.main')
    def test__update_hand_split(self, mock_main):
        """If sent a split hand, _update_hand() should update the 
        split row of the table.
        """
        hands = [
            cards.Hand([cards.Card(11, 0),]),
            cards.Hand([cards.Card(11, 3),]),
        ]
        player = players.Player(hands, name='spam', chips=100)
        player2 = players.Player(name='eggs', chips=100)
        new_data = [
            [player, 100, 20, 'J♣', 'Splits hand.'], 
            ['  \u2514\u2500', '', 20, 'J♠ 5♣', 'Hits.'],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'], 
        ]
        exp = call().send(('update', new_data))
        
        data = [
            [player, 100, 20, 'J♣', 'Splits hand.'], 
            ['  \u2514\u2500', '', 20, 'J♠', 'Splits hand.'],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'], 
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        hands[1].append(cards.Card(5, 0))
        ui._update_hand(player, hands[1], 'Hits.')
        act = mock_main.mock_calls[-1]
        ui.end()
        
        self.assertEqual(exp, act)
    
    @patch('blackjack.termui.main')
    def test_cleanup(self, mock_main):
        """When called, cleanup() should clear the bet, hand, and 
        event field of every row in the data table, then send it to 
        the UI.
        """
        hands = [
            cards.Hand([cards.Card(11, 0),]),
            cards.Hand([cards.Card(11, 3),]),
        ]
        player = players.Player(hands, name='spam', chips=100)
        player2 = players.Player(hands, name='eggs', chips=100)
        new_data = [
            [player, 100, '', '', ''],
            [player2, 100, '', '', ''],
        ]
        exp = call().send(('update', new_data))
        
        data = [
            [player, 100, 20, 'J♣', 'Splits hand.'], 
            ['  \u2514\u2500', '', 20, 'J♠', 'Splits hand.'],
            [player2, 100, 20, '3♣ 4♣', 'Takes hand.'], 
        ]
        ui = cli.TableUI()
        ui.ctlr.data = data
        ui.start()
        ui.cleanup()
        act = mock_main.mock_calls[-1]
        
        self.assertEqual(exp, act)
    
    
    # Input method tests.
    @patch('blackjack.termui.main')
    def test___prompt_calls(self, mock_main):
        """When called, _prompt() should send the UI a prompt for user 
        input and return the result.
        """
        exp_call = call().send(('input', 'spam', 'y'))
        
        
        ui = cli.TableUI()
        ui.start()
        act_resp = ui._prompt('spam', 'y')
        act_call = mock_main.mock_calls[-1]
        ui.end()
        
        self.assertEqual(exp_call, act_call)
    
    @patch('blackjack.termui.main')
    @patch('blackjack.cli.TableUI._prompt')
    def test_nextgame_prompt(self, mock_main, _):
        """When called, mextgame_prompt() should prompt the user 
        whether they would like to play another game. The response 
        should be returned.
        """
        exp_resp = model.IsYes('y')
        exp_call = call('Play another round? [yn] >', 'y')
        
        ui = cli.TableUI()
        mock_main.return_value = 'y'
        ui.start()
        act_resp = ui.nextgame_prompt()
        ui.end()
        act_call = mock_main.mock_calls[-1]
        
        self.assertEqual(exp_resp.value, act_resp.value)
        self.assertEqual(exp_call, act_call)
    
    @patch('blackjack.termui.main')
    def test_nextgame_prompt_(self, mock_main):
        """If the user responds with an invalid value, the prompt 
        should be repeated.
        """
        exp_resp = model.IsYes('n')
        
        ui = cli.TableUI()
        mock_main.return_value = (item for item in [None, None, 'z', ' ', 'n'])
        ui.start()
        act_resp = ui.nextgame_prompt()
        ui.end()
        
        self.assertEqual(exp_resp.value, act_resp.value)


class UITestCase(ut.TestCase):
    tmp = '{:<15} {:<15} {:<}\n'
    
    def test_initial_banners(self):
        """When a new UI object is initialized, it should print the 
        name of the application and the column headers to stdout.
        """
        lines = [
            '\n',
            'BLACKJACK!\n',
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
        hands = (
            cards.Hand([cards.Card(7, 0),]),
            cards.Hand([cards.Card(7, 1),]),
        )
        player = players.AutoPlayer(hands, name='Terry')
        with capture() as (out, err):
            ui.update('split', player, [20, 180])
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
    
    def test_update_end_split_wins(self):
        """Given an event that a player won, the 
        update() method should print victory to stdout.
        """
        fmt = '{} ({})'.format(40, 220)
        expected = self.tmp.format('Graham', 'Wins.', fmt)
        
        ui = cli.UI(True)
        p1 = players.AutoPlayer(name='Graham')
        with capture() as (out, err):
            ui.update('splitpayout', p1, [40, 220])
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_end_loses(self):
        """Given an event that a player lost, the 
        update() method should print loss to stdout.
        """
        expected = self.tmp.format('Graham', 'Loses.', '')
        
        ui = cli.UI(True)
        p1 = players.AutoPlayer(name='Graham')
        with capture() as (out, err):
            ui.update('lost', p1, None)
        actual = out.getvalue()
        
        self.assertEqual(expected, actual)
    
    def test_update_end_split_loses(self):
        """Given an event that a player lost, the 
        update() method should print loss to stdout.
        """
        expected = self.tmp.format('Graham', 'Loses.', '')
        
        ui = cli.UI(True)
        p1 = players.AutoPlayer(name='Graham')
        with capture() as (out, err):
            ui.update('splitlost', p1, None)
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
    
    def test_update_end_split_tie(self):
        """Given an event that a player tied the dealer on a split 
        hand, the update() method should print the tie to stdout.
        """
        fmt = '{} ({})'.format(20, 220)
        expected = self.tmp.format('Graham', 'Stand-off.', fmt)
        
        ui = cli.UI(True)
        p1 = players.AutoPlayer(name='Graham')
        with capture() as (out, err):
            ui.update('splittie', p1, [20, 220])
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
    def test_update_deal(self, mock_term):
        """Given an event that a player has bet, the update() method 
        should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 220)
        hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 0),
        ])
        expected = call().send(('shuffled',))
        
        ui = cli.DynamicUI()
        ui.update('deal', player, hand)
        ui.update('shuffled', player, '')
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_doubled(self, mock_term):
        """Given an event that a player has doubled down, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 200)
        expected = call().send(('doubled', player, 40))
        
        ui = cli.DynamicUI()
        ui.update('doubled', player, [40, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_flip(self, mock_term):
        """Given an event that a dealer has flipped a card, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 220)
        hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 0),
        ])
        expected = call().send(('flip', player, hand))
        
        ui = cli.DynamicUI()
        ui.update('flip', player, hand)
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_hit(self, mock_term):
        """Given an event that a player has hit, the update() method 
        should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 220)
        hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(3, 0),
            cards.Card(4, 0),
        ])
        expected = call().send(('hit', player, hand))
        
        ui = cli.DynamicUI()
        ui.update('hit', player, hand)
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_insure(self, mock_term):
        """Given an event that a player has bought insurance, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 200)
        expected = call().send(('insure', player, 30))
        
        ui = cli.DynamicUI()
        ui.update('insure', player, [30, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_insurepay(self, mock_term):
        """Given an event that a player has split, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 200)
        expected = call().send(('insurepay', player, 40))
        
        ui = cli.DynamicUI()
        ui.update('insurepay', player, [40, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
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
    def test_update_lost(self, mock_term):
        """Given an event that a player has lost, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 200)
        expected = call().send(('lost', player))
        
        ui = cli.DynamicUI()
        ui.update('lost', player, [40, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_payout(self, mock_term):
        """Given an event that a player has split, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 200)
        expected = call().send(('payout', player, 40))
        
        ui = cli.DynamicUI()
        ui.update('payout', player, [40, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_remove(self, mock_term):
        """Given an event that a player has left the game, 
        the update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 220)
        expected = call().send(('remove', player))
        
        ui = cli.DynamicUI()
        ui.update('remove', player, '')
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_split(self, mock_term):
        """Given an event that a player has split, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 200)
        expected = call().send(('split', player, 40))
        
        ui = cli.DynamicUI()
        ui.update('split', player, [40, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_splitpayout(self, mock_term):
        """Given an event that a player has split and won, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 200)
        expected = call().send(('splitpayout', player, 40))
        
        ui = cli.DynamicUI()
        ui.update('splitpayout', player, [40, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_splitlost(self, mock_term):
        """Given an event that a player has split and lost, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 200)
        expected = call().send(('splitlost', player, 0))
        
        ui = cli.DynamicUI()
        ui.update('splitlost', player, [0, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_splittie(self, mock_term):
        """Given an event that a player has split and tied, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 200)
        expected = call().send(('splittie', player, 20))
        
        ui = cli.DynamicUI()
        ui.update('splittie', player, [20, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.run_terminal')
    def test_update_stand(self, mock_term):
        """Given an event that a player has hit, the update() method 
        should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 220)
        hand = cards.Hand([
            cards.Card(11, 3),
            cards.Card(3, 0),
            cards.Card(4, 0),
        ])
        expected = call().send(('stand', player, hand))
        
        ui = cli.DynamicUI()
        ui.update('stand', player, hand)
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)

    @patch('blackjack.cli.run_terminal')
    def test_update_tie(self, mock_term):
        """Given an event that a player has tied, the 
        update() method should print that event to stdout.
        """
        player = players.AutoPlayer([], 'Graham', 200)
        expected = call().send(('tie', player, 20))
        
        ui = cli.DynamicUI()
        ui.update('tie', player, [20, 200])
        actual = mock_term.mock_calls[-1]
        
        self.assertEqual(expected, actual)
    
    
    # Test DynamicUI.input().
    @patch('blackjack.cli.run_terminal')
    def test_input_doubledown_call(self, mock_term):
        """Given an event that there should be a doubledown prompt, 
        input() should call for the the prompt.
        """
        ex_call = call().send(('doubledown_prompt',))
        ex_return = model.IsYes(True)
        
        ui = cli.DynamicUI()
        ac_return = ui.input('doubledown')
        ac_call = mock_term.mock_calls[-1]
        
        self.assertEqual(ex_call, ac_call)
    
    @patch('blackjack.cli.run_terminal')
    def test_input_doubledown_return(self, mock_term):
        """Given an event that there should be a doubledown prompt, 
        input() should return the response to the prompt.
        """
        ex_return = model.IsYes(True)
        
        mock_term.return_value = (item for item in [None, ex_return])
        ui = cli.DynamicUI()
        ac_return = ui.input('doubledown')
        
        self.assertEqual(ex_return, ac_return)

    @patch('blackjack.cli.run_terminal')
    def test_input_hit_call(self, mock_term):
        """Given an event that there should be a hit prompt, 
        input() should call for the the prompt.
        """
        ex_call = call().send(('hit_prompt',))
        ex_return = model.IsYes(True)
        
        ui = cli.DynamicUI()
        ac_return = ui.input('hit')
        ac_call = mock_term.mock_calls[-1]
        
        self.assertEqual(ex_call, ac_call)
    
    @patch('blackjack.cli.run_terminal')
    def test_input_hit_return(self, mock_term):
        """Given an event that there should be a hit prompt, 
        input() should return the response to the prompt.
        """
        ex_return = model.IsYes(True)
        
        mock_term.return_value = (item for item in [None, ex_return])
        ui = cli.DynamicUI()
        ac_return = ui.input('hit')
        
        self.assertEqual(ex_return, ac_return)

    @patch('blackjack.cli.run_terminal')
    def test_input_insure_call(self, mock_term):
        """Given an event that there should be an insure prompt, 
        input() should call for the the prompt.
        """
        ex_call = call().send(('insure_prompt',))
        ex_return = model.IsYes(True)
        
        ui = cli.DynamicUI()
        ac_return = ui.input('insure')
        ac_call = mock_term.mock_calls[-1]
        
        self.assertEqual(ex_call, ac_call)
    
    @patch('blackjack.cli.run_terminal')
    def test_input_insure_return(self, mock_term):
        """Given an event that there should be an insure prompt, 
        input() should return the response to the prompt.
        """
        ex_return = model.IsYes(True)
        
        mock_term.return_value = (item for item in [None, ex_return])
        ui = cli.DynamicUI()
        ac_return = ui.input('insure')
        
        self.assertEqual(ex_return, ac_return)

    @patch('blackjack.cli.run_terminal')
    def test_input_nextgame_prompt_call(self, mock_term):
        """Given an event that there should be a new game prompt, 
        input() should call for the prompt.
        """
        ex_call = call().send(('nextgame_prompt',))
        ex_return = model.IsYes(True)
        
        ui = cli.DynamicUI()
        ac_return = ui.input('nextgame')
        ac_call = mock_term.mock_calls[-1]
        
        self.assertEqual(ex_call, ac_call)
    
    @patch('blackjack.cli.run_terminal')
    def test_input_nextgame_prompt_return(self, mock_term):
        """Given an event that there should be a new game prompt, 
        input() should return the response to the prompt.
        """
        ex_return = model.IsYes(True)
        
        mock_term.return_value = (item for item in [None, ex_return])
        ui = cli.DynamicUI()
        ac_return = ui.input('nextgame')
        
        self.assertEqual(ex_return, ac_return)
    
    @patch('blackjack.cli.run_terminal')
    def test_input_split_call(self, mock_term):
        """Given an event that there should be a split prompt, 
        input() should call for the the prompt.
        """
        ex_call = call().send(('split_prompt',))
        ex_return = model.IsYes(True)
        
        ui = cli.DynamicUI()
        ac_return = ui.input('split')
        ac_call = mock_term.mock_calls[-1]
        
        self.assertEqual(ex_call, ac_call)
    
    @patch('blackjack.cli.run_terminal')
    def test_input_split_return(self, mock_term):
        """Given an event that there should be a split prompt, 
        input() should return the response to the prompt.
        """
        ex_return = model.IsYes(True)
        
        mock_term.return_value = (item for item in [None, ex_return])
        ui = cli.DynamicUI()
        ac_return = ui.input('split')
        
        self.assertEqual(ex_return, ac_return)


class run_terminalTestCase(ut.TestCase):
    bold = '\x1b[1m'
    ascii = '\x1b(B'
    default = '\x1b[m'
    h_tmp = '{:<14} {:>7} {:>3} {:<27} {:<}'
    r_tmp = '{:<14} {:>7} {:>3} {:<27} {:<}'
    locs = ['\x1b[{};1H', '\x1b[{};16H', '\x1b[{};24H', 
            '\x1b[{};28H', '\x1b[{};56H']
    fmts = ['{:<14}', '{:>7}', '{:>3}', '{:<27}', '{:<24}']
    
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
    def test__update_hand(self, mock_print):
        """When given a player, a hand, and a message, _update_hand() 
        should print those updates to the screen.
        """
        hand1 = cards.Hand([
            cards.Card(11, 3),
            cards.Card(1, 2),
        ])
        hand2 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(1, 1),
        ])
        playerlist = [
            players.Player((hand1,), name='spam', chips=200),
            players.Player((hand2,), name='eggs', chips=200),            
        ]
        expected = [
            call(self.locs[3].format(5) + self.fmts[3].format(hand1)),
            call(self.locs[4].format(5) + self.fmts[4].format('spam')),
        ]
        
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        ctlr.data[0][3] = str(hand1[0])
        ctlr.data[1][3] = str(hand2[0])
        ctlr._update_hand(playerlist[0], hand1, 'spam')
        actual = mock_print.mock_calls[-2:]
        del term
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test__update_bet(self, mock_print):
        """When given a player, a bet, and a message, _update_bet() 
        should print those updates to the screen.
        """
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        expected = [
            call(self.locs[1].format(5) + self.fmts[1].format(200)),
            call(self.locs[2].format(5) + self.fmts[2].format(20)),
            call(self.locs[4].format(5) + self.fmts[4].format('spam')),
        ]
        
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        ctlr.data[0][1] = 220
        ctlr._update_bet(playerlist[0], 20, 'spam')
        actual = mock_print.mock_calls[-3:]
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
        player_tmp = '{:<14}'
        chips_tmp = '{:>7}'
        event_tmp = '{:<24}'
        player_loc = '\x1b[{};1H'
        chips_loc = '\x1b[{};16H'
        event_loc = '\x1b[{};56H'
        expected = [
            call(player_loc.format(5) + player_tmp.format(playerlist[0])),
            call(chips_loc.format(5) + chips_tmp.format(playerlist[0].chips)),
            call(event_loc.format(5) + event_tmp.format('Joins game.')),
            call(player_loc.format(6) + player_tmp.format(playerlist[1])),
            call(chips_loc.format(6) + chips_tmp.format(playerlist[1].chips)),
            call(event_loc.format(6) + event_tmp.format('Joins game.')),
        ]
        
        term = cli.run_terminal()
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        actual = mock_print.mock_calls[-6:]
        del term

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_remove(self, mock_print):
        """When sent a remove message, run_terminal() should display a 
        message that the player has left.
        """
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        expected = [
            call(self.locs[4].format(5) + self.fmts[4].format('Walks away.')),
        ]
        expected_row = ['', '', '', '', '']
        
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('remove', playerlist[0]))
        actual = mock_print.mock_calls[-1:]
        del term
        actual_row = ctlr.data[0]

        self.assertEqual(expected, actual)
        self.assertEqual(expected_row, actual_row)
    
    @patch('blackjack.cli.print')
    def test_join_data(self, mock_print):
        """When sent a join message, run_terminal() should update 
        the data table in the TerminalController with the row for 
        that player.
        """
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        expected = [[p, p.chips, '', '', 'Joins game.'] for p in playerlist]
        
        try:
            ctlr = cli.TerminalController(Terminal())
            term = cli.run_terminal(ctlr=ctlr)
            next(term)
            term.send(('init', len(playerlist)))
            term.send(('join', playerlist[0]))
            term.send(('join', playerlist[1]))
            actual = ctlr.data
            del term
        except Exception as ex:
            del term
            raise ex
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_buyin_data(self, mock_print):
        """When sent a buyin message, run_terminal() should update 
        the data table in TerminalController withe the new chips and 
        bet totals.
        """
        expected = [200, '20', 'Bets.']
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('buyin', playerlist[0], 20))
        del term
        actual = [ctlr.data[0][1], ctlr.data[0][2], ctlr.data[0][4]]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_double(self, mock_print):
        """When sent an double message, run_terminal() should update 
        the player's bet and announce the decision.
        """
        expected = [200, '20', 'Doubles down.']
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('doubled', playerlist[0], 20))
        del term
        actual = [ctlr.data[0][1], ctlr.data[0][2], ctlr.data[0][4]]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_flip(self, mock_print):
        """When sent a flip message, run_terminal() should display
        the player's hand and event message in the player's row.
        """        
        hand0 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(1, 1),
        ])
        expected = [str(hand0), 'Flips card.']        
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())      
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('flip', playerlist[0], hand0))
        del term
        actual = [ctlr.data[0][3], ctlr.data[0][4]]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_hit(self, mock_print):
        """When sent a hit message, run_terminal() should display
        the player's hand in the player's row.
        """
        hand0 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(1, 1),
        ])
        expected = [str(hand0), 'Hits.']        
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())      
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('hit', playerlist[0], hand0))
        del term
        actual = [ctlr.data[0][3], ctlr.data[0][4]]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_insured(self, mock_print):
        """When sent an insure message, run_terminal() should update 
        the player's bet and announce the decision.
        """
        expected = [200, '20', 'Buys insurance.']
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('insure', playerlist[0], 20))
        del term
        actual = [ctlr.data[0][1], ctlr.data[0][2], ctlr.data[0][4]]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_insurepay(self, mock_print):
        """When sent an insurepay message, run_terminal() should update 
        the player's chips and announce the result.
        """
        expected = [200, '', 'Insurance pays 20.']
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('insurepay', playerlist[0], 20))
        del term
        actual = [ctlr.data[0][1], ctlr.data[0][2], ctlr.data[0][4]]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_lost(self, mock_print):
        """When sent an lost message, run_terminal() should update 
        the player's chips and announce the result.
        """
        expected = [200, '', 'Loses.']
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('lost', playerlist[0]))
        del term
        actual = [ctlr.data[0][1], ctlr.data[0][2], ctlr.data[0][4]]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_payout(self, mock_print):
        """When sent an payout message, run_terminal() should update 
        the player's chips and announce the result.
        """
        expected = [200, '', 'Wins 20.']
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('payout', playerlist[0], 20))
        del term
        actual = [ctlr.data[0][1], ctlr.data[0][2], ctlr.data[0][4]]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_shuffle(self, mock_print):
        """When sent a shuffle message, run_terminal() should display
        the event message in the dealer's row.
        """        
        hand0 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(1, 1),
        ])
        expected = ['Shuffles deck.']        
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())      
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('shuffled',))
        del term
        actual = [ctlr.data[0][4]]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_split(self, mock_print):
        """When sent an split message, run_terminal() should update 
        the player's bet and announce the decision.
        """
        hands = [
            cards.Hand([cards.Card(11, 0),]),
            cards.Hand([cards.Card(11, 3),]),
        ]
        playerlist = [
            players.Player(hands, name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
            players.Player(name='baked beans', chips=200),            
        ]
        expected = [
            [playerlist[0], 200, 20, str(hands[0]),'Splits.'],
            ['  \u2514\u2500', '', 20, str(hands[1]), ''],
            [playerlist[1], 200, '', '', 'Joins game.'],
            [playerlist[2], 200, '', '', 'Joins game.'],
        ]
        
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('join', playerlist[2]))
        term.send(('split', playerlist[0], 20))
        del term
        actual = ctlr.data

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_stand(self, mock_print):
        """When sent a stand message, run_terminal() should display
        the player's hand in the player's row.
        """
        hand0 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(1, 1),
        ])
        expected = [str(hand0), 'Stands.']        
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())      
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('stand', playerlist[0], hand0))
        del term
        actual = [ctlr.data[0][3], ctlr.data[0][4]]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_stand_bust(self, mock_print):
        """When sent a stand message, run_terminal() should display
        the player's hand in the player's row.
        """
        hand0 = cards.Hand([
            cards.Card(11, 0),
            cards.Card(3, 1),
            cards.Card(10, 1),
        ])
        expected = [str(hand0), 'Busts.']        
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())      
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('stand', playerlist[0], hand0))
        del term
        actual = [ctlr.data[0][3], ctlr.data[0][4]]
        
        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_splitpayout(self, mock_print):
        """When sent an splitpayout message, run_terminal() should 
        update the player's chips and announce the result.
        """
        expected = [
            [200, 20, 'ham'],
            ['', '', 'Wins 20.'],
        ]
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        data = [
            [playerlist[0], 200, 20, 'bacon', 'ham'],
            ['  \u2514\u2500', '', '20', 'bacon', 'ham'],
            [playerlist[1], 200, 20, 'bacon', 'ham'],
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        ctlr.data = data
        term.send(('splitpayout', playerlist[0], 20))
        del term
        actual = [
            [ctlr.data[0][1], ctlr.data[0][2], ctlr.data[0][4]],
            [ctlr.data[1][1], ctlr.data[1][2], ctlr.data[1][4]],
        ]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_splitlost(self, mock_print):
        """When sent an splitlost message, run_terminal() should 
        update the player's chips and announce the result.
        """
        expected = [
            [200, 20, 'ham'],
            ['', '', 'Loses.'],
        ]
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        data = [
            [playerlist[0], 200, 20, 'bacon', 'ham'],
            ['  \u2514\u2500', '', '20', 'bacon', 'ham'],
            [playerlist[1], 200, 20, 'bacon', 'ham'],
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        ctlr.data = data
        term.send(('splitlost', playerlist[0], 0))
        del term
        actual = [
            [ctlr.data[0][1], ctlr.data[0][2], ctlr.data[0][4]],
            [ctlr.data[1][1], ctlr.data[1][2], ctlr.data[1][4]],
        ]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_splittie(self, mock_print):
        """When sent an splittie message, run_terminal() should 
        update the player's chips and announce the result.
        """
        expected = [
            [200, 20, 'ham'],
            ['', '', 'Ties. Keeps 20.'],
        ]
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        data = [
            [playerlist[0], 200, 20, 'bacon', 'ham'],
            ['  \u2514\u2500', '', '20', 'bacon', 'ham'],
            [playerlist[1], 200, 20, 'bacon', 'ham'],
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        ctlr.data = data
        term.send(('splittie', playerlist[0], 20))
        del term
        actual = [
            [ctlr.data[0][1], ctlr.data[0][2], ctlr.data[0][4]],
            [ctlr.data[1][1], ctlr.data[1][2], ctlr.data[1][4]],
        ]

        self.assertEqual(expected, actual)
    
    @patch('blackjack.cli.print')
    def test_tie(self, mock_print):
        """When sent an tie message, run_terminal() should update 
        the player's chips and announce the result.
        """
        expected = [200, '', 'Ties. Keeps 20.']
        
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        term.send(('tie', playerlist[0], 20))
        del term
        actual = [ctlr.data[0][1], ctlr.data[0][2], ctlr.data[0][4]]

        self.assertEqual(expected, actual)
    
    
    # Input messages.
    @patch('blessed.Terminal.inkey')
    @patch('blackjack.cli.print')
    def test_double_down_prompt(self, mock_print, mock_inkey):
        """When sent a double_down_prompt message, run_terminal() 
        should prompt the user for whether they'd like to hit and 
        return the response.
        """
        prompt_tmp = '\x1b[{row};1H{}'
        expd_print = [
            call(prompt_tmp.format('Double down? (Y/n) > _', row=8)),
            call('\x1b[8;1H' + (' ' * 80)),
        ]
        expd_return = model.IsYes(True)
        
        mock_inkey.return_value = True
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        actl_return = term.send(('doubledown_prompt',))
        actl_print = mock_print.mock_calls[-2:]
        del term
        
        self.assertEqual(expd_print, actl_print)
        self.assertEqual(expd_return.value, actl_return.value)
    
    @patch('blessed.Terminal.inkey')
    @patch('blackjack.cli.print')
    def test_hit_prompt(self, mock_print, mock_inkey):
        """When sent a hit_prompt message, run_terminal() should 
        prompt the user for whether they'd like to hit and return 
        the response.
        """
        prompt_tmp = '\x1b[{row};1H{}'
        expd_print = [
            call(prompt_tmp.format('Hit? (Y/n) > _', row=8)),
            call('\x1b[8;1H' + (' ' * 80)),
        ]
        expd_return = model.IsYes(True)
        
        mock_inkey.return_value = True
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        actl_return = term.send(('hit_prompt',))
        actl_print = mock_print.mock_calls[-2:]
        del term
        
        self.assertEqual(expd_print, actl_print)
        self.assertEqual(expd_return.value, actl_return.value)
    
    @patch('blessed.Terminal.inkey')
    @patch('blackjack.cli.print')
    def test_hit_prompt(self, mock_print, mock_inkey):
        """When sent a insure_prompt message, run_terminal() should 
        prompt the user for whether they'd like to insure and return 
        the response.
        """
        prompt_tmp = '\x1b[{row};1H{}'
        expd_print = [
            call(prompt_tmp.format('Insure? (Y/n) > _', row=8)),
            call('\x1b[8;1H' + (' ' * 80)),
        ]
        expd_return = model.IsYes(True)
        
        mock_inkey.return_value = True
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        actl_return = term.send(('insure_prompt',))
        actl_print = mock_print.mock_calls[-2:]
        del term
        
        self.assertEqual(expd_print, actl_print)
        self.assertEqual(expd_return.value, actl_return.value)
    
    @patch('blessed.Terminal.inkey')
    @patch('blackjack.cli.print')
    def test_hit_prompt(self, mock_print, mock_inkey):
        """When sent a split_prompt message, run_terminal() should 
        prompt the user for whether they'd like to split and return 
        the response.
        """
        prompt_tmp = '\x1b[{row};1H{}'
        expd_print = [
            call(prompt_tmp.format('Split? (Y/n) > _', row=8)),
            call('\x1b[8;1H' + (' ' * 80)),
        ]
        expd_return = model.IsYes(True)
        
        mock_inkey.return_value = True
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        actl_return = term.send(('split_prompt',))
        actl_print = mock_print.mock_calls[-2:]
        del term
        
        self.assertEqual(expd_print, actl_print)
        self.assertEqual(expd_return.value, actl_return.value)
    
    @patch('blessed.Terminal.inkey')
    @patch('blackjack.cli.print')
    def test_nextgame_prompt(self, mock_print, mock_inkey):
        """When sent a nextgame_prompt message, run_terminal() should 
        prompt the user for whether they'd like another round of 
        blackjack and return the response.
        """
        prompt_tmp = '\x1b[{row};1H{}'
        expd_print = [
            call(prompt_tmp.format('Another round? (Y/n) > _', row=8)),
            call('\x1b[8;1H' + (' ' * 80)),
            call('\x1b[7;1H' + ('\u2500' * 80)),
            call(self.locs[0].format(5) + self.fmts[0].format('spam')),
            call(self.locs[0].format(6) + self.fmts[0].format('eggs')),
            call(self.locs[2].format(5) + self.fmts[2].format('')),
            call(self.locs[3].format(5) + self.fmts[3].format('')),
            call(self.locs[4].format(5) + self.fmts[4].format('')),
            call(self.locs[2].format(6) + self.fmts[2].format('')),
            call(self.locs[3].format(6) + self.fmts[3].format('')),
            call(self.locs[4].format(6) + self.fmts[4].format('')),
        ]
        expd_return = model.IsYes(True)
        
        mock_inkey.return_value = True
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        for row in ctlr.data:
            row[2], row[3], row[4] = '42', 'bacon', 'ham'
        actl_return = term.send(('nextgame_prompt',))
        actl_print = mock_print.mock_calls[-11:]
        del term
        
        self.assertEqual(expd_print, actl_print)
        self.assertEqual(expd_return.value, actl_return.value)
    
    @patch('blessed.Terminal.inkey')
    @patch('blackjack.cli.print')
    def test_nextgame_prompt_with_split(self, mock_print, mock_inkey):
        """When sent a nextgame_prompt message, run_terminal() should 
        prompt the user for whether they'd like another round of 
        blackjack and return the response.
        """
        prompt_tmp = '\x1b[{row};1H{}'
        expd_print = [
            call(prompt_tmp.format('Another round? (Y/n) > _', row=9)),
            call('\x1b[9;1H' + (' ' * 80)),
            call('\x1b[8;1H' + (' ' * 80)),
            call('\x1b[7;1H' + ('\u2500' * 80)),
            call(self.locs[0].format(5) + self.fmts[0].format('spam')),
            call(self.locs[0].format(6) + self.fmts[0].format('eggs')),
            call(self.locs[1].format(5) + self.fmts[1].format('200')),
            call(self.locs[2].format(5) + self.fmts[2].format('')),
            call(self.locs[3].format(5) + self.fmts[3].format('')),
            call(self.locs[4].format(5) + self.fmts[4].format('')),
            call(self.locs[1].format(6) + self.fmts[1].format('200')),
            call(self.locs[2].format(6) + self.fmts[2].format('')),
            call(self.locs[3].format(6) + self.fmts[3].format('')),
            call(self.locs[4].format(6) + self.fmts[4].format('')),
        ]
        expd_return = model.IsYes(True)
        
        mock_inkey.return_value = True
        playerlist = [
            players.Player(name='spam', chips=200),
            players.Player(name='eggs', chips=200),            
        ]
        table = [
            [playerlist[0], '220', '20', 'bacon', 'ham'],
            ['  \u2514\u2500', '', '20', 'bacon', 'ham'],
            [playerlist[1], '220', '20', 'bacon', 'ham'],
        ]
        ctlr = cli.TerminalController(Terminal())
        term = cli.run_terminal(ctlr=ctlr)
        next(term)
        term.send(('init', len(playerlist)))
        term.send(('join', playerlist[0]))
        term.send(('join', playerlist[1]))
        ctlr.data = table
        actl_return = term.send(('nextgame_prompt',))
        actl_print = mock_print.mock_calls[-14:]
        del term
        
        self.assertEqual(expd_print, actl_print)
        self.assertEqual(expd_return.value, actl_return.value)