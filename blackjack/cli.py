"""
cli
~~~

The module contains the basic classes used by blackjack for handling 
a command line interface.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import argparse

from blessed import Terminal

from blackjack import cards, game, model, players


# Objects and functions for advanced terminal control.
def run_terminal(is_interactive=False):
    """A coroutine to run the dynamic terminal UI.
    
    :param is_interactive: (Optional.) Whether the terminal should 
        expect user input. This is mainly used for automated testing.
    :yield: None.
    :ytype: None.
    """
    term = Terminal()
    ctlr = TerminalController(term)
    with term.fullscreen(), term.hidden_cursor():
        while True:
            method, *args = yield
            getattr(ctlr, method)(*args)
            if is_interactive:
                term.inkey()


class TerminalController:
    """A controller to handle UI events sent to the run_terminal 
    coroutine.
    """
    def __init__(self, term):
        self.term = term
        self.headers = ('Player', 'Chips', 'Bet', 'Hand', 'Event')
        self.playerlist = []
        self.h_tmp = '{:<14} {:>7} {:>3} {:<27} {:<}'
        self.r_tmp = '{:<14} {:>7} {:>3} {:<27} {:<}'
    
    def buyin(self, player, bet):
        """A player bets on a round.
        
        :param player: The player making the bet.
        :param bet: The amount of the bet.
        :return: None.
        :rtype: None.
        """
        msg_tmp = '{:<' + str(self.term.width - 56) + '}'
        row = self.playerlist.index(player) + 4
        chips = self.term.move(row, 15) + '{:>7}'.format(player.chips)
        bet = self.term.move(row, 23) +'{:>3}'.format(bet)
        msg = self.term.move(row, 55) + msg_tmp.format('Bets.')
        print(chips + bet + msg)
    
    def deal(self, player, hand):
        """A player was dealt a hand.
        
        :param player: The player who was dealt the hand.
        :param hand: The hand that was dealt.
        :return: None.
        :rtype: None.
        """
        msg_tmp = '{:<' + str(self.term.width - 56) + '}'
        row = self.playerlist.index(player) + 4
        handstr = self.term.move(row, 27) + ' '.join(str(card) for card in hand)
        msg = self.term.move(row, 55) + msg_tmp.format('Takes hand.')
        print(handstr + msg)
    
    def doubled(self, player, bet):
        """The player doubles down.
        
        :param player: The player doubling down.
        :param bet: The player's new bet total.
        :param chips: The player's updated chips total.
        :return: None.
        :rtype: None.
        """
        msg_tmp = '{:<' + str(self.term.width - 56) + '}'
        row = self.playerlist.index(player) + 4
        chips = self.term.move(row, 15) + '{:>7}'.format(player.chips)
        bet = self.term.move(row, 23) + '{:>3}'.format(bet)
        msg = self.term.move(row, 55) + msg_tmp.format('Doubles down.')
        print(chips + bet + msg)
    
    def init(self, seats):
        """Blackjack has started.
        
        :param seats: The number of players that can be in the game.
        :return: None.
        :rtype: None.
        """
        for i in range(seats):
            self.playerlist.append(None)
        print(self.term.bold('BLACKJACK'))
        print(self.term.move_down + self.r_tmp.format(*self.headers))
        print('\u2500' * self.term.width)
        for line in range(seats):
            print()
        print('\u2500' * self.term.width)
    
    def insure(self, player, bet):
        """The player purchased insurance.
        
        :param player: The player purchasing insurance.
        :param bet: The player's new bet total.
        :param chips: The player's updated chips total.
        :return: None.
        :rtype: None.
        """
        msg_tmp = '{:<' + str(self.term.width - 56) + '}'
        row = self.playerlist.index(player) + 4
        chips = self.term.move(row, 15) + '{:>7}'.format(player.chips)
        bet = self.term.move(row, 23) + '{:>3}'.format(bet)
        msg = self.term.move(row, 55) + msg_tmp.format('Buys insurance.')
        print(chips + bet + msg)
    
    def join(self, player):
        """A new player joined the game.
        
        :param player: The player joining the game.
        :return: None.
        :rtype: None.
        """
        try:
            index = self.playerlist.index(None)
        except ValueError:
            reason = 'No empty seats in the player list.'
            raise ValueError(reason)
        else:
            self.playerlist[index] = player
            row = index + 4
            msg = 'Joins game.'
            line = (player.name, player.chips, '', '', msg)
            print(self.term.move(row, 0) + self.r_tmp.format(*line))
        
    def split(self, player, bet):
        """The player split their hand.
        
        :param player: The player splitting.
        :param bet: The player's new bet total.
        :param chips: The player's updated chips total.
        :return: None.
        :rtype: None.
        """
        msg_tmp = '{:<' + str(self.term.width - 56) + '}'
        row = self.playerlist.index(player) + 4
        chips = self.term.move(row, 15) + '{:>7}'.format(player.chips)
        bet = self.term.move(row, 23) + '{:>3}'.format(bet)
        msg = self.term.move(row, 55) + msg_tmp.format('Splits.')
        print(chips + bet + msg)



# UI objects.
class DynamicUI(game.BaseUI):
    def __init__(self, is_interactive=False):
        """Initialize an instance of the class."""
        self.rows = []
        self.t = run_terminal(is_interactive)
        next(self.t)
    
    def enter(self, seats):
        self.t.send(('init', seats))
    
    def update(self, event, player, detail):
        if event == 'buyin':
            self.t.send((event, player, detail[0]))
        elif event == 'deal':
            self.t.send((event, player, detail))
#         elif == 'doubled':
#             self.t.send(event, player, detail[0])
        elif event == 'insure':
            self.t.send((event, player, detail[0]))
        elif event == 'join':
            self.t.send((event, player))
        elif event == 'split':
            self.t.send((event, player, detail[0]))


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
        if event == 'payout':
            fmt = '{} ({})'.format(*detail)
            msg = self.tmp.format(player, 'Wins.', fmt)
        if event == 'remove':
            msg = self.tmp.format(player, 'Walks away.', '')
        if event == 'shuffled':
            msg = self.tmp.format(player, 'Shuffled deck.', '')
        if event == 'split':
            lines = [
                self.tmp.format(player, 'Hand split.', get_handstr(detail[0])),
                self.tmp.format('', '', get_handstr(detail[1])),
            ]
            msg = '\n'.join(lines)
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
    g.start()
    g.deal()

def test():
    playerlist = [
        players.Player(name='spam', chips=200),
        players.Player(name='eggs', chips=200),            
    ]
    term = run_terminal(True)
    next(term)
    term.send(('init', len(playerlist)))
    for player in playerlist:
        term.send(('join', player))
    term.send(('end'))
    
    

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
        