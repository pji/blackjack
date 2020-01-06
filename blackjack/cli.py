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

from blackjack import cards, game, players


# UI object.
class UI(game.BaseUI):
    tmp = '{:<15} {:<15} {:<}'
    
    def __init__(self, silent: bool = False) -> None:
        if not silent:
            self.enter()
    
    def enter(self):
        print()
        print('BLACKJACK!')
        print()
        print(self.tmp.format('Player', 'Action', 'Hand'))
        print('\u2500' * 50)
    
    def exit(self):
        print('\u2500' * 50)
        print()
    
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
        if event == 'flip':
            msg = self.tmp.format(player, 'Flipped card.', handstr)
        if event == 'hit':
            msg = self.tmp.format(player, 'Hit.', handstr)
        if event == 'payout':
            fmt = '{} ({})'.format(*detail)
            msg = self.tmp.format(player, 'Wins.', fmt)
        if event == 'remove':
            msg = self.tmp.format(player, 'Walks away.', '')
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
        if not msg:
            raise NotImplementedError
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
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    player = players.AutoPlayer(name='Player', chips=200)
    g = game.Game(deck, dealer, (player,), ui=ui, buyin=2)
    g.start()
    g.deal()
    g.play()
    ui.exit()    


def two_player():
    ui = UI()
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    p1 = players.AutoPlayer(name='John', chips=200)
    p2 = players.AutoPlayer(name='Michael', chips=152)
    g = game.Game(deck, dealer, (p1, p2), ui=ui, buyin=2)
    g.start()
    g.deal()
    g.play()
    ui.exit()    


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Blackjack')
    p.add_argument('-d', '--dealer_only', help='Just a dealer.', 
                   action='store_true')
    p.add_argument('-1', '--one_player', help='One player.', 
                   action='store_true')
    p.add_argument('-2', '--two_player', help='Two player.', 
                   action='store_true')
    args = p.parse_args()
    
    if args.dealer_only:
        dealer_only()
    if args.one_player:
        one_player()
    if args.two_player:
        two_player()
