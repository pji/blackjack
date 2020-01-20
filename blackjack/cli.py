"""
cli
~~~

The module contains the basic classes used by blackjack for handling 
a command line interface.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import argparse
from collections import namedtuple, OrderedDict
from copy import deepcopy
import sys
from time import sleep
import traceback as tb
from typing import Sequence

from blessed import Terminal

from blackjack import cards, game, model, players, termui


# Objects and functions for advanced terminal control.
FieldInfo = namedtuple('FieldInfo', 'loc fmt')

def run_terminal(is_interactive=False, ctlr=None):
    """A coroutine to run the dynamic terminal UI.
    
    :param is_interactive: (Optional.) Whether the terminal should 
        expect user input. This is mainly used for automated testing.
    :yield: None.
    :ytype: None.
    """
    term = None
    if not ctlr:
        term = Terminal()
        ctlr = TerminalController(term, is_interactive)
    else:
        term = ctlr.term
    resp = None
    with term.fullscreen(), term.hidden_cursor():
        while True:
            method, *args = yield resp
            resp = getattr(ctlr, method)(*args)
            if is_interactive:
                sleep(.15)


class TerminalController:
    """A controller to handle UI events sent to the run_terminal 
    coroutine.
    """
    def __init__(self, term, is_interactive=False):
        self.term = term
        self.playerlist = []
        self.h_tmp = '{:<14} {:>7} {:>3} {:<27} {:<}'
        self.r_tmp = '{:<14} {:>7} {:>3} {:<27} {:<}'
        self.is_interactive = is_interactive
        self.fields = OrderedDict([
            ('Player', FieldInfo(0, '{:<14}'),),
            ('Chips', FieldInfo(15, '{:>7}'),),
            ('Bet', FieldInfo(23, '{:>3}'),),
            ('Hand', FieldInfo(27, '{:<27}'),),
            ('Event', FieldInfo(55, '{:<' + str(self.term.width-56) + '}'),),
        ])
        self.data = []
    
    
    # Update messages.
    def _update_bet(self, player, bet, msg):
        """The game event updates the player's bet.
        
        :param player: The player making the bet.
        :param bet: The amount of the bet.
        :param msg: The event's explanation.
        :return: None.
        :rtype: None.
        """
        table = [row[:] for row in self.data]
        row = [row[0] for row in table].index(player)
        
        if bet:
            bet = str(int(bet))
            if len(bet) > 3:
                bet = '{}e{}'.format(bet[0], len(bet))
        table[row][1] = player.chips
        table[row][2] = bet
        table[row][4] = msg
        self._update_table(table)
    
    def _update_hand(self, player, hand, msg):
        """The game event updates the player's hand.
        
        :param player: The player who was dealt the hand.
        :param hand: The hand that was dealt.
        :param msg: The event's explanation.
        :return: None.
        :rtype: None.
        """
        table = [row[:] for row in self.data]
        row = [row[0] for row in table].index(player)
        
        # Handle split hands.
        if len(player.hands) == 2:
            row += player.hands.index(hand)
        
        table[row][3] = str(hand)
        table[row][4] = msg
        self._update_table(table)
    
    def _update_table(self, data):
        if len(data) < len(self.data):
            y = len(self.data) + 5
            print(self.term.move(y, 0) + (' ' * self.term.width))
            while len(data) < len(self.data):
                _ = self.data.pop()
                y = len(self.data) + 5
                print(self.term.move(y, 0) + (' ' * self.term.width))
        elif len(data) > len(self.data):
            y = len(data) + 4
            print(self.term.move(y, 0) + ('\u2500' * self.term.width))
            while len(data) > len(self.data):
                y = len(self.data) + 4
                print(self.term.move(y, 0) + ' ' * self.term.width)
                self.data.append(['', '', '', '', ''])
        for row in range(len(data)):
            for col in range(len(self.fields)):
                if data[row][col] != self.data[row][col]:
                    fields = list(self.fields.keys())
                    y = row + 4
                    x, fmt = self.fields[fields[col]]
                    print(self.term.move(y, x) + fmt.format(data[row][col]))
        self.data = data
    
    def buyin(self, player, bet):
        """A player bets on a round.
        
        :param player: The player making the bet.
        :param bet: The amount of the bet.
        :return: None.
        :rtype: None.
        """
        self._update_bet(player, bet, 'Bets.')
    
    def deal(self, player, hand):
        """A player was dealt a hand.
        
        :param player: The player who was dealt the hand.
        :param hand: The hand that was dealt.
        :return: None.
        :rtype: None.
        """
        self._update_hand(player, hand, 'Takes hand.')
    
    def doubled(self, player, bet):
        """The player doubles down.
        
        :param player: The player doubling down.
        :param bet: The player's new bet total.
        :return: None.
        :rtype: None.
        """
        self._update_bet(player, bet, 'Doubles down.')
    
    def flip(self, dealer, hand):
        """The dealer flipped a card.
        
        :param dealer: The dealer who was dealt the hand.
        :param hand: The hand that was dealt.
        :return: None.
        :rtype: None.
        """
        self._update_hand(dealer, hand, 'Flips card.')
    
    def hit(self, player, hand):
        """A player hits.
        
        :param player: The player who was dealt the hand.
        :param hand: The hand that was dealt.
        :return: None.
        :rtype: None.
        """
        self._update_hand(player, hand, 'Hits.')
    
    def init(self, seats):
        """Blackjack has started.
        
        :param seats: The number of players that can be in the game.
        :return: None.
        :rtype: None.
        """
        for i in range(seats):
            self.data.append(['', '', '', '', ''])
        print(self.term.bold('BLACKJACK'))
        print(self.term.move_down + self.r_tmp.format(*self.fields.keys()))
        print('\u2500' * self.term.width)
        for line in range(seats):
            print()
        print('\u2500' * self.term.width)
    
    def insure(self, player, bet):
        """The player purchased insurance.
        
        :param player: The player purchasing insurance.
        :param bet: The player's new bet total.
        :return: None.
        :rtype: None.
        """
        self._update_bet(player, bet, 'Buys insurance.')
    
    def insurepay(self, player, bet):
        """The player gets an insurance pay out.
        
        :param player: The player who bought insurance.
        :param bet: How much the player recieved.
        :return: None.
        :rtype: None.
        """
        msg = f'Insurance pays {bet}.'
        self._update_bet(player, '', msg)
    
    def join(self, player):
        """A new player joined the game.
        
        :param player: The player joining the game.
        :return: None.
        :rtype: None.
        """
        playerlist = [row[0] for row in self.data]
        msg = 'Joins game.'
        try:
            index = playerlist.index('')
        except ValueError:
            reason = ('Player tried to join, but there are no empty '
                      f'seats at the table. {playerlist}')
            raise ValueError(reason)
        else:
            table = [row[:] for row in self.data]
            table[index][0] = player
            table[index][1] = player.chips
            table[index][4] = msg
            
            self._update_table(table)
            self.playerlist = [row[0] for row in self.data]
            
    def lost(self, player):
        """The player loses the hand.
        
        :param player: The player who lost.
        :return: None.
        :rtype: None.
        """
        msg = f'Loses.'
        self._update_bet(player, '', msg)
    
    def payout(self, player, bet):
        """The player wins the hand.
        
        :param player: The player who won.
        :param bet: How much the player won.
        :return: None.
        :rtype: None.
        """
        msg = f'Wins {bet}.'
        self._update_bet(player, '', msg)
    
    def remove(self, player):
        """A player leaves the game.
        
        :param player: The player who left.
        :return: None
        :rtype: None
        """
        msg = 'Walks away.'
        data = [row[:] for row in self.data]
        row = [row[0] for row in data].index(player)
        data[row][4] = msg
        self._update_table(data)
        self.data[row] = ['', '', '', '', '']
    
    def shuffled(self):
        """The dealer shuffles."""
        msg = 'Shuffles deck.'
        data = [row[:] for row in self.data]
        data[0][4] = msg
        self._update_table(data)
    
    def split(self, player, bet):
        """The player split their hand.
        
        :param player: The player splitting.
        :param bet: The player's new bet total.
        :return: None.
        :rtype: None.
        """
        row = [row[0] for row in self.data].index(player)
        table = [row[:] for row in self.data[0:row + 1]]
        table.append(['  \u2514\u2500', '', '', '', ''])
        for new_row in self.data[row + 1:]:
            table.append(new_row[:])
        table[row][2] = bet
        table[row][3] = str(player.hands[0])
        table[row][4] = 'Splits.'
        table[row + 1][2] = bet
        table[row + 1][3] = str(player.hands[1])
        self._update_table(table)
    
    def splitlost(self, player, bet):
        """The player split their hand and lost.
        
        :param player: The player splitting.
        :param bet: The player's new bet total.
        :return: None.
        :rtype: None.
        """
        msg = 'Loses.'
        table = [row[:] for row in self.data]
        row = [row[0] for row in table].index(player)
        row += 1
        table[row][2] = ''
        table[row][4] = msg
        self._update_table(table)
    
    def splitpayout(self, player, bet):
        """The player split their hand and won.
        
        :param player: The player splitting.
        :param bet: The player's new bet total.
        :return: None.
        :rtype: None.
        """
        msg = f'Wins {bet}.'
        table = [row[:] for row in self.data]
        row = [row[0] for row in table].index(player)
        row += 1
        table[row][2] = ''
        table[row][4] = msg
        self._update_table(table)
    
    def splittie(self, player, bet):
        """The player split their hand and tied.
        
        :param player: The player splitting.
        :param bet: The player's new bet total.
        :return: None.
        :rtype: None.
        """
        msg = f'Ties. Keeps {bet}.'
        table = [row[:] for row in self.data]
        row = [row[0] for row in table].index(player)
        row += 1
        table[row][2] = ''
        table[row][4] = msg
        self._update_table(table)
    
    def stand(self, player, hand):
        """A player hits.
        
        :param player: The player who was dealt the hand.
        :param hand: The hand that was dealt.
        :return: None.
        :rtype: None.
        """
        scores = [score for score in hand.score() if score <= 21]
        if scores:
            self._update_hand(player, hand, 'Stands.')
        else:
            self._update_hand(player, hand, 'Busts.')
        
    def tie(self, player, bet):
        """The player ties the hand.
        
        :param player: The player who won.
        :param bet: How much the player kept.
        :return: None.
        :rtype: None.
        """
        msg = f'Ties. Keeps {bet}.'
        self._update_bet(player, '', msg)
    
    
    # Input messages.
    def _yesno_prompt(self, msg) -> model.IsYes:
        """Prompt the user with a yes/no question.
        
        :param msg: The question to prompt with.
        :return: The user's decision.
        :rtype: model.IsYes
        """
        row = len(self.data) + 5
        clearline = self.term.move(row, 0) + (' ' * self.term.width)
        msg = self.term.move(row, 0) + f'{msg} (Y/n) > _'
        is_yes = None
        while not is_yes:
            print(clearline)
            if self.is_interactive:
                sleep(.2)
            print(msg)
            with self.term.cbreak():
                resp = self.term.inkey()
            try:
                is_yes = model.IsYes(resp)
            except ValueError:
                pass
        print(clearline)
        return is_yes
    
    def doubledown_prompt(self) -> model.IsYes:
        """Does the user want to double down?
        
        :return: The user's decision.
        :rtype: model.IsYes
        """
        return self._yesno_prompt('Double down?')
    
    def hit_prompt(self) -> model.IsYes:
        """Does the user want to hit?
        
        :return: The user's decision.
        :rtype: model.IsYes
        """
        return self._yesno_prompt('Hit?')
    
    def insure_prompt(self) -> model.IsYes:
        """Does the user want to insure the hand?
        
        :return: The user's decision.
        :rtype: model.IsYes
        """
        return self._yesno_prompt('Insure?')
    
    def nextgame_prompt(self) -> model.IsYes:
        """Does the user want to play again?
        
        :return: The user's decision.
        :rtype: model.IsYes
        """
        resp = self._yesno_prompt('Another round?')
        if resp.value:
            # Undo splits.
            playerlist = [row[0] for row in self.data]
            while '  \u2514\u2500' in playerlist:
                index = playerlist.index('  \u2514\u2500')
                _ = playerlist.pop(index)
                _ = self.data.pop(index)
                y = len(self.data) + 5
                print(self.term.move(y, 0) + (' ' * self.term.width))
            y = len(self.data) + 4
            print(self.term.move(y, 0) + ('\u2500' * self.term.width))
            for index in range(len(playerlist)):
                y = index + 4
                print(self.term.move(y, self.fields['Player'].loc) 
                      + self.fields['Player'].fmt.format(playerlist[index]))
        
            # Clear previous round.
            table = [row[:] for row in self.data]
            for row in table:
                row[1] = row[0].chips
                row[2] = ''
                row[3] = ''
                row[4] = ''
            self._update_table(table)
        return resp
    
    def split_prompt(self) -> model.IsYes:
        """Does the user want to split the hand?
        
        :return: The user's decision.
        :rtype: model.IsYes
        """
        return self._yesno_prompt('Split?')


# UI objects.
class DynamicUI(game.BaseUI):
    def __init__(self, is_interactive=False):
        """Initialize an instance of the class."""
        self.rows = []
        self.t = run_terminal(is_interactive)
        next(self.t)
    
    def enter(self, seats):
        self.t.send(('init', seats))
    
    def input(self, event, details=None, default=None):
        """Get user input from the UI.
        
        :param event: The event you need input for.
        :param details: (Optional.) Details specific to the event.
        :param default: (Optional.) The default value for the input. 
            This is mainly to make input easier to test.
        :return: The input received from the UI.
        :rtype: Any. (May need an response object in the future.)
        """
        resp = None
        if event == 'doubledown':
            resp = self.t.send(('doubledown_prompt',))
        elif event == 'hit':
            resp = self.t.send(('hit_prompt',))
        elif event == 'insure':
            resp = self.t.send(('insure_prompt',))
        elif event == 'nextgame':
            resp = self.t.send(('nextgame_prompt',))
        elif event == 'split':
            resp = self.t.send(('split_prompt',))
        else:
            reason = f'Dynamic UI does not recognize {event}.'
            raise ValueError(reason)
        return resp
    
    def update(self, event, player, detail):
        if event == 'buyin':
            self.t.send((event, player, detail[0]))
        elif event == 'deal':
            self.t.send((event, player, detail))
        elif event == 'doubled':
            self.t.send((event, player, detail[0]))
        elif event == 'flip':
            self.t.send((event, player, detail))
        elif event == 'hit':
            self.t.send((event, player, detail))
        elif event == 'insure':
            self.t.send((event, player, detail[0]))
        elif event == 'insurepay':
            self.t.send((event, player, detail[0]))
        elif event == 'join':
            self.t.send((event, player))
        elif event == 'lost':
            self.t.send((event, player))
        elif event == 'payout':
            self.t.send((event, player, detail[0]))
        elif event == 'remove':
            self.t.send((event, player))
        elif event == 'shuffled':
            self.t.send((event,))
        elif event == 'split':
            self.t.send((event, player, detail[0]))
        elif event == 'splitlost':
            self.t.send((event, player, detail[0]))
        elif event == 'splitpayout':
            self.t.send((event, player, detail[0]))
        elif event == 'splittie':
            self.t.send((event, player, detail[0]))
        elif event == 'stand':
            self.t.send((event, player, detail))
        elif event == 'tie':
            self.t.send((event, player, detail[0]))
        else:
            reason = f'Event not recognized. {event}'
            raise NotImplementedError(reason)


class TableUI(game.EngineUI):
    """A table-based terminal UI for blackjack."""
    # General operation methods.
    def __init__(self, ctlr: termui.TerminalController = None, 
                 seats: int = 1) -> None:
        """Initialize and instance of the class.
        
        :param ctlr: (Optional.) The TerminalController object running 
            the UI.
        :param seats: (Optional.) The number of seats that will be 
            available for the game.
        """
        self.seats = seats
        if not ctlr:
            ctlr = self._make_ctlr()
        self.ctlr = ctlr
        self.loop = None
    
    def _make_ctlr(self):
        """Returns a termui.Table object for blackjack."""
        fields = (
            ('Player', '{:<14}'),
            ('Chips', '{:>7}'),
            ('Bet', '{:>3}'),
            ('Hand', '{:<27}'),
            ('Event', '{:<23}'),
        )
        return termui.Table('Blackjack', fields, rows=self.seats)
    
    def end(self):
        """End the UI loop gracefully."""
        self.loop.close()
    
    def start(self, is_interactive=False):
        """Start the UI."""
        self.loop = termui.main(self.ctlr, is_interactive)
        next(self.loop)
        self.loop.send(('draw',))
    
    
    # Input methods.
    def _prompt(self, prompt, default):
        return self.loop.send(('input', prompt, default))
    
    def doubledown_prompt(self) -> model.IsYes:
        """Ask user if they want to double down."""    
    
    def hit_prompt(self) -> model.IsYes:
        """Ask user if they want to hit."""    
    
    def insure_prompt(self) -> model.IsYes:
        """Ask user if they want to insure."""    
    
    def nextgame_prompt(self) -> model.IsYes:
        """Ask user if they want to play another round."""
        prompt = 'Play another round? [yn] >'
        default = 'y'
        valid = None
        while not isinstance(valid, model.IsYes):
            resp = self._prompt(prompt, default)
            try:
                valid = model.IsYes(resp)
            except ValueError:
                pass
        return valid
    
    def split_prompt(self) -> model.IsYes:
        """Ask user if they want to split."""    
    
    
    # Update methods.
    def _get_field_index(self, needed: Sequence[str]) -> list:
        """Get the indices the given fields of the data table.
        
        :param needed: The names of the fields you need the indexes 
            for.
        :return: A list of the indices.
        :rtype: list
        """
        fields = [field.name for field in self.ctlr.fields]
        return [fields.index(field) for field in needed]
    
    def _get_player_row_and_data(self, player: players.Player) -> tuple:
        """Get the data table row for the given player.
        
        :param player: The player to get the row for.
        :return: An index and a copy of the data table.
        :rtype: tuple
        """
        # Get the player's row to update.
        # Since termui.Table determines which fields to updata by 
        # looking for changes in the data table, it's very important 
        # that we create a copy of data here.
        data = [row[:] for row in self.ctlr.data]
        playerlist = [row[0] for row in data]
        row = playerlist.index(player)
        return row, data
    
    def _update_bet(self, player, bet, event, split=False):
        """The player's bet and chips information needs to be 
        updated.
        
        :param player: The player whose row to update.
        :param bet: The player's bet.
        :param event: The event that occurred.
        :param split: Whether the update is for the split hand.
        :return: None.
        :rtype: NoneType
        """
        row, data = self._get_player_row_and_data(player)
        if split and len(player.hands) == 2:
            row += 1
        
        affected_fields = ('Chips', 'Bet', 'Event')
        i_chips, i_bet, i_event = self._get_field_index(affected_fields)
        
        if not split:
            data[row][i_chips] = player.chips
        data[row][i_bet] = bet
        data[row][i_event] = event
        self.loop.send(('update', data))
    
    def _update_event(self, player, event):
        """The player's event information needs to be updated.
        """
        row, data = self._get_player_row_and_data(player)
        
        affected_fields = ('Event',)
        i_event, = self._get_field_index(affected_fields)
        
        data[row][i_event] = event
        self.loop.send(('update', data))
    
    def _update_hand(self, player, hand, event):
        """The player's hand information needs to be updated."""
        row, data = self._get_player_row_and_data(player)
        if len(player.hands) == 2:
            if player.hands.index(hand) == 1:
                row += 1
        
        affected_fields = ('Hand', 'Event')
        i_hand, i_event = self._get_field_index(affected_fields)
        
        data[row][i_hand] = str(hand)
        data[row][i_event] = event
        self.loop.send(('update', data))
    
    def bet(self, player, bet):
        """Player places initial bet."""
        self._update_bet(player, bet, 'Bets.')
    
    def cleanup(self):
        """Clean up information from the previous round."""
        data = [row[:] for row in self.ctlr.data]
        affected = ['Player', 'Bet', 'Hand', 'Event']
        i_play, i_bet, i_hand, i_event = self._get_field_index(affected)
        data = [row for row in data if isinstance(row[i_play], players.Player)]
        for row in data:
            row[i_bet] = ''
            row[i_hand] = ''
            row[i_event] = ''
        self.loop.send(('update', data))
    
    def deal(self, player, hand):
        """Player recieves initial hand."""
        self._update_hand(player, hand, 'Takes hand.')
    
    def doubledown(self, player, bet):
        """Player doubles down."""
        self._update_bet(player, bet, 'Doubles down.')
    
    def flip(self, player, hand):
        """Player flips a card."""
        self._update_hand(player, hand, 'Flips card.')
    
    def hit(self, player, hand):
        """Player hits."""
        self._update_hand(player, hand, 'Hits.')
    
    def insures(self, player, bet):
        """Player insures their hand."""
        self._update_bet(player, bet, f'Buys {bet} insurance.')
    
    def insurepay(self, player, bet):
        """Insurance is paid to player."""
        self._update_bet(player, bet, f'Insurance pays {bet}.')
    
    def joins(self, player):
        """Player joins the game.
        
        :param player: The player to add to the game.
        :return: None.
        :rtype: NoneType.
        """
        row, data = self._get_player_row_and_data('')
        affected = ['Player', 'Chips', 'Event']
        i_play, i_chip, i_event = self._get_field_index(affected)
        
        data[row][i_play] = player
        data[row][i_chip] = player.chips
        data[row][i_event] = 'Sits down.'
        
        self.loop.send(('update', data))
    
    def leaves(self, player):
        """Player leaves the game.
        
        :param player: The player to remove from the game.
        :return: None.
        :rtype: NoneType.
        """
        row, data = self._get_player_row_and_data(player)
        affected = ['Player', 'Chips', 'Bet', 'Hand', 'Event']
        i_play, i_chip, i_bet, i_hand, i_event = self._get_field_index(affected)
        
        # Send leaving message to UI.
        data[row][i_chip] = ''
        data[row][i_bet] = ''
        data[row][i_hand] = ''
        data[row][i_event] = 'Walks away.'
        self.loop.send(('update', data))
        
        # Remove the player from the data table.
        self.ctlr.data[row][i_play] = ''
    
    def loses(self, player):
        """Player loses."""
        self._update_bet(player, '', 'Loses.')
    
    def loses_split(self, player):
        """Player loses on their split hand."""
        self._update_bet(player, '', 'Loses.', True)
    
    def shuffles(self, player):
        """The deck is shuffled."""
        self._update_event(player, 'Shuffles the deck.')
    
    def splits(self, player, bet):
        """Player splits their hand."""
        row, data = self._get_player_row_and_data(player)
        affected = ['Player', 'Chips', 'Bet', 'Hand', 'Event']
        i_play, i_chip, i_bet, i_hand, i_event = self._get_field_index(affected)
        
        # Update existing row.
        data[row][i_chip] = player.chips
        data[row][i_bet] = bet
        data[row][i_hand] = str(player.hands[0])
        data[row][i_event] = 'Splits hand.'
        
        # Build the new split row and add it.
        new_row = ['' for field in range(len(self.ctlr.fields))]
        new_row[i_play] = '  \u2514\u2500'
        new_row[i_bet] = bet
        new_row[i_hand] = str(player.hands[1])
        data.insert(row + 1, new_row)
        
        self.loop.send(('update', data))
    
    def stand(self, player, hand):
        """Player stands."""
        self._update_hand(player, hand, 'Stands.')
    
    def tie(self, player, bet):
        """Player ties."""
        self._update_bet(player, '', f'Ties {bet}.')
    
    def ties_split(self, player, bet):
        """Player ties."""
        self._update_bet(player, '', f'Ties {bet}.', True)
    
    def wins(self, player, bet):
        """Player wins."""
        self._update_bet(player, '', f'Wins {bet}.')
    
    def wins_split(self, player, bet):
        """Player wins on their split hand."""
        self._update_bet(player, '', f'Wins {bet}.', True)


class UI(game.BaseUI):
    tmp = '{:<15} {:<15} {:<}'
    
    def __init__(self, silent: bool = False) -> None:
        if not silent:
            print()
            print('BLACKJACK!')
    
    def enter(self):
        print()
        print(self.tmp.format('Player', 'Action', 'Hand'))
        print('\u2500' * 50)
    
    def exit(self):
        print('\u2500' * 50)
        print()
    
    def input(self, event, details=None, default=None):
        """Get user input from the UI.
        
        :param event: The event you need input for.
        :param details: (Optional.) Details specific to the event.
        :param default: (Optional.) The default value for the input. 
            This is mainly to make input easier to test.
        :return: The input received from the UI.
        :rtype: Any. (May need an response object in the future.)
        """
        prompt = None
        if event == 'doubledown':
            prompt = 'Double down? Y/n > '
        elif event == 'hit':
            prompt = 'Hit? Y/n > '
        elif event == 'insure':
            prompt = 'Insure? Y/n > '
        elif event == 'nextgame':
            prompt = 'Another round? Y/n > '
        elif event == 'split':
            prompt = 'Split? Y/n > '
        if not prompt:
            reason = 'Invalid event sent to UI.input().'
            raise NotImplementedError(reason)
        return self._yesno_prompt(prompt)
    
    def _yesno_prompt(self, prompt:str, default: bool = True) -> model.IsYes:
        """Prompt the user for a yes/no answer."""
        response = None
        
        # Repeat the prompt until you get a valid response.
        while not response:
            untrusted = input(prompt)
            
            # Allow the response to default to true. Saves typing when 
            # playing. 
            if not untrusted:
                untrusted = default
            
            # Determine if the input is valid.
            try:
                response = model.IsYes(untrusted)
            
            # If it's not valid, the ValueError will be caught, 
            # response won't be set, so the prompt will be repeated.
            except ValueError:
                pass
        
        return response
        
    def update(self, event:str, player:str, detail: object) -> None:
        """Update the UI.
        
        :param event: The event the UI needs to display.
        :param player: The player name involved in the event.
        :param hand: The hand to display.
        :return: None.
        :rtype: None.
        """
        def get_handstr(hand):
            return ' '.join([str(card) for card in hand])
        
        msg = None
        if detail and isinstance(detail, cards.Hand):
            handstr = get_handstr(detail)
        if event == 'buyin':
            fmt = '{} ({})'.format(*detail)
            msg = self.tmp.format(player, 'Initial bet.', fmt)
        if event == 'deal':
            msg = self.tmp.format(player,  'Initial deal.', handstr)
        if event == 'doubled':
            fmt = '{} ({})'.format(*detail)
            msg = self.tmp.format(player, 'Doubled down.', fmt)
        if event == 'flip':
            msg = self.tmp.format(player, 'Flipped card.', handstr)
        if event == 'hit':
            msg = self.tmp.format(player, 'Hit.', handstr)
        if event == 'insured':
            fmt = '{} ({})'.format(*detail)
            msg = self.tmp.format(player, 'Insured.', fmt)
        if event == 'insurepay':
            fmt = '{} ({})'.format(*detail)
            msg = self.tmp.format(player, 'Insurance pay out.', fmt)
        if event == 'join':
            phrase = 'Walks up.'
            if player.name == 'You':
                phrase = 'Walk up.'
            msg = self.tmp.format(player, phrase, '')
        if event == 'lost':
            msg = self.tmp.format(player, 'Loses.', '')
        if event == 'payout':
            fmt = '{} ({})'.format(*detail)
            msg = self.tmp.format(player, 'Wins.', fmt)
        if event == 'remove':
            msg = self.tmp.format(player, 'Walks away.', '')
        if event == 'shuffled':
            msg = self.tmp.format(player, 'Shuffled deck.', '')
        if event == 'split':
            hands = player.hands
            lines = [
                self.tmp.format(player, 'Hand split.', get_handstr(hands[0])),
                self.tmp.format('', '', get_handstr(hands[1])),
            ]
            msg = '\n'.join(lines)
        if event == 'splitlost':
            msg = self.tmp.format(player, 'Loses.', '')
        if event == 'splitpayout':
            fmt = '{} ({})'.format(*detail)
            msg = self.tmp.format(player, 'Wins.', fmt)
        if event == 'splittie':
            fmt = '{} ({})'.format(*detail)
            msg = self.tmp.format(player, 'Stand-off.', fmt)
        if event == 'stand':
            scores = [score for score in detail.score() if score <= 21]
            try:
                score = scores[-1]
            except IndexError:
                score = 'Bust.'
            msg = self.tmp.format(player, 'Stand.', score)
        if event == 'tie':
            fmt = '{} ({})'.format(*detail)
            msg = self.tmp.format(player, 'Stand-off.', fmt)
        if not msg:
            reason = 'Invalid event sent to UI.update().' + msg
            raise NotImplementedError(reason)
        print(msg)


# Command scripts.
def dealer_only():
    ui = UI()
    g = game.Game(ui=ui)
    g.deck.shuffle()
    g.deal()
    g.play()
    ui.exit()


def one_player():
    ui = UI()
    play = True
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    player = players.AutoPlayer(name='Player', chips=200)
    g = game.Game(deck, dealer, (player,), ui=ui, buyin=2)
    while play:
        ui.enter()
        g.start()
        g.deal()
        g.play()
        g.end()
        ui.exit()
        play = ui.input('nextgame').value


def two_player():
    ui = UI()
    play = True
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    p1 = players.AutoPlayer(name='John', chips=200)
    p2 = players.BetterPlayer(name='Michael', chips=200)
    g = game.Game(deck, dealer, (p1, p2), ui=ui, buyin=2)
    g.new_game()
    while play:
        ui.enter()
        g.start()
        g.deal()
        g.play()
        g.end()
        ui.exit()
        play = ui.input('nextgame').value


def three_player():
    ui = UI()
    play = True
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    p1 = players.AutoPlayer(name='John', chips=200)
    p2 = players.BetterPlayer(name='Michael', chips=200)
    p3 = players.UserPlayer(name='You', chips=200)
    g = game.Game(deck, dealer, (p1, p2, p3), ui=ui, buyin=2)
    g.new_game()
    while play:
        ui.enter()
        g.start()
        g.deal()
        g.play()
        g.end()
        ui.exit()
        play = ui.input('nextgame').value


def four_player():
    ui = UI()
    play = True
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    playerlist = []
    for index in range(4):
        playerlist.append(players.make_player())
    g = game.Game(deck, dealer, playerlist, ui=ui, buyin=2)
    g.new_game()
    while play:
        ui.enter()
        g.start()
        g.deal()
        g.play()
        g.end()
        ui.exit()
        play = ui.input('nextgame').value


def dui():
    ui = DynamicUI(True)
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    playerlist = []
    for index in range(4):
        playerlist.append(players.make_player(bet=20))
    playerlist.append(players.UserPlayer(name='You', chips=200))
    g = game.Game(deck, dealer, playerlist, ui=ui, buyin=20)
    ui.enter(len(playerlist) + 1)
    g.new_game()
    play = True
    while play:
        try:
            g.start()
            g.deal()
            g.play()
            g.end()
            play = ui.input('nextgame').value
        except Exception as ex:
            with open('exception.txt', 'w') as fh:
                fh.write(str(ex.args))
                tb_str = ''.join(tb.format_tb(ex.__traceback__))
                fh.write(tb_str)
            raise ex


def test():
    try:
        ui = TableUI(seats=5)
        deck = cards.Deck.build(6)
        deck.shuffle()
        deck.random_cut()
    #     deck = cards.Deck([
    #         cards.Card(10, 0, cards.DOWN),
    #         cards.Card(10, 0, cards.DOWN),
    #         cards.Card(10, 0, cards.DOWN),
    #         cards.Card(6, 0, cards.DOWN),
    #         cards.Card(2, 0, cards.DOWN),
    #         cards.Card(8, 0, cards.DOWN),
    #         cards.Card(10, 0, cards.DOWN),
    #         cards.Card(10, 0, cards.DOWN),
    #         cards.Card(7, 0, cards.DOWN),
    #         cards.Card(10, 0, cards.DOWN),
    #     ])
        deck.size = 1
        dealer = players.Dealer(name='Dealer')
        playerlist = []
#         playerlist = [players.AutoPlayer(name='Spam', chips=100),]
        for index in range(4):
            playerlist.append(players.make_player(chips=1000))
        g = game.Engine(deck, dealer, playerlist, ui=ui, buyin=20)
        ui.start(True)
        g.new_game()
        play = True
        while play:
            g.start()
            g.deal()
            g.play()
            g.end()
            play = ui.nextgame_prompt().value
            if play:
                ui.cleanup()
    except Exception as ex:
        with open('exception.txt', 'w') as fh:
            fh.write(str(ex.args))
            tb_str = ''.join(tb.format_tb(ex.__traceback__))
            fh.write(tb_str)
        raise ex


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Blackjack')
    p.add_argument('-d', '--dealer_only', help='Just a dealer game.', 
                   action='store_true')
    p.add_argument('-1', '--one_player', help='One player game.', 
                   action='store_true')
    p.add_argument('-2', '--two_player', help='Two player game.', 
                   action='store_true')
    p.add_argument('-3', '--three_player', help='Three player game.', 
                   action='store_true')
    p.add_argument('-4', '--four_player', help='Four player game.', 
                   action='store_true')
    p.add_argument('-D', '--dui', help='Dynamic UI game.', 
                   action='store_true')
    p.add_argument('-p', '--players', help='Number of random players.', 
                   action='store', type=int)
    p.add_argument('-u', '--user', help='Add a human player.', 
                   action='store_true')
    p.add_argument('-c', '--chips', help='Number of starting chips.', 
                   action='store', type=int, default=200)
    p.add_argument('-C', '--cost', help='Hand bet amount.', 
                   action='store', type=int, default=20)
    p.add_argument('-t', '--test', help='Run current test.', 
                   action='store_true')
    args = p.parse_args()
    
    if args.dealer_only:
        dealer_only()
    elif args.one_player:
        one_player()
    elif args.two_player:
        two_player()
    elif args.three_player:
        three_player()
    elif args.four_player:
        four_player()
    elif args.dui:
        dui()
    elif args.test:
        test()
    else:
        if args.chips > 9999999:
            reason = 'Cannot start with more than 9999999 chips.'
            raise ValueError(reason)
        if args.cost > 99999999:
            reason = 'Bets cannot be more than 99999999.'
            raise ValueError(reason)
        
        playerlist = []
        for _ in range(int(args.players)):
            playerlist.append(players.make_player(args.chips))
        if args.user:
            playerlist.append(players.UserPlayer(name='You', chips=args.chips))
        
        deck = cards.Deck.build(6)
        deck.shuffle()
        deck.random_cut()
        ui = DynamicUI(True)
        g = game.Game(deck, None, playerlist, ui, args.cost)
        ui.enter(len(playerlist) + 1)
        g.new_game()
        
        play_again = True
        while play_again:
            try:
                g.start()
                g.deal()
                g.play()
                g.end()
                play_again = ui.input('nextgame').value
            except Exception as ex:
                with open('exception.txt', 'w') as fh:
                    fh.write(str(ex.args))
                    tb_str = ''.join(tb.format_tb(ex.__traceback__))
                    fh.write(tb_str)
                raise ex
        