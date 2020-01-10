"""
cli
~~~

The module contains the basic classes used by blackjack for handling 
a command line interface.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import argparse
from functools import partial

from blackjack import cards, game, model, players


# UI object.
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
            reason = 'Invalid event sent to UI.update().'
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
    while play:
        ui.enter()
        g.start()
        g.deal()
        g.play()
        g.end()
        ui.exit()
        play = ui.input('nextgame').value

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
    p.add_argument('-p', '--players', help='Number of random players.', 
                   action='store')
    p.add_argument('-u', '--user', help='Add a human player.', 
                   action='store_true')
    p.add_argument('-c', '--chips', help='Number of starting chips.', 
                   action='store')
    p.add_argument('-C', '--cost', help='Hand bet amount.', 
                   action='store')
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
        
        play_again = True
        while play_again:
            ui.enter()
            g.start()
            g.deal()
            g.play()
            g.end()
            ui.exit()
            play_again = ui.input('nextgame').value
        