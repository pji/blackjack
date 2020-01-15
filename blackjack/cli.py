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

from blessed import Terminal

from blackjack import cards, game, model, players


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
                      'seats at the table.')
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
        if event == 'nextgame':
            resp = self.t.send(('nextgame_prompt',))
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
        elif event == 'join':
            self.t.send((event, player))
        elif event == 'lost':
            self.t.send((event, player))
        elif event == 'payout':
            self.t.send((event, player, detail[0]))
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
        playerlist.append(players.make_player())
    g = game.Game(deck, dealer, playerlist, ui=ui, buyin=2)
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
    ui = DynamicUI(True)
#     deck = cards.Deck.build(6)
#     deck.shuffle()
#     deck.random_cut()
    deck = cards.Deck([
        cards.Card(10, 0, cards.DOWN),
        cards.Card(10, 0, cards.DOWN),
        cards.Card(10, 0, cards.DOWN),
        cards.Card(6, 0, cards.DOWN),
        cards.Card(2, 0, cards.DOWN),
        cards.Card(8, 0, cards.DOWN),
        cards.Card(10, 0, cards.DOWN),
        cards.Card(10, 0, cards.DOWN),
        cards.Card(7, 0, cards.DOWN),
        cards.Card(10, 0, cards.DOWN),
    ])
    dealer = players.Dealer(name='Dealer')
    playerlist = [players.AutoPlayer(name='Spam', chips=100),]
#     for index in range(4):
#         playerlist.append(players.make_player())
    g = game.Game(deck, dealer, playerlist, ui=ui, buyin=2)
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
                   action='store')
    p.add_argument('-u', '--user', help='Add a human player.', 
                   action='store_true')
    p.add_argument('-c', '--chips', help='Number of starting chips.', 
                   action='store')
    p.add_argument('-C', '--cost', help='Hand bet amount.', 
                   action='store')
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
        chips = 200
        if args.chips:
            chips = float(args.chips)
        buyin = 2
        if args.cost:
            buyin = float(args.cost)
        
        playerlist = []
        for _ in range(int(args.players)):
            playerlist.append(players.make_player(chips))
        if args.user:
            playerlist.append(players.UserPlayer(name='You', chips=chips))
        
        deck = cards.Deck.build(6)
        deck.shuffle()
        deck.random_cut()
        ui = UI()
        g = game.Game(deck, None, playerlist, ui, buyin)
        g.new_game()
        
        play_again = True
        while play_again:
            ui.enter()
            g.start()
            g.deal()
            g.play()
            g.end()
            ui.exit()
            play_again = ui.input('nextgame').value
        