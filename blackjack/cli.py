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
class UI:
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
    
    def update(self, event:str, player:str, hand: cards.Hand = None) -> None:
        """Update the UI.
        
        :param event: The event the UI needs to display.
        :param player: The player name involved in the event.
        :param hand: The hand to display.
        :return: None.
        :rtype: None.
        """
        msg = None
        if hand:
            handstr = ' '.join([str(card) for card in hand])
        if event == 'deal':
            msg = self.tmp.format(player,  'Initial deal.', handstr)
        if event == 'flip':
            msg = self.tmp.format(player, 'Flipped card.', handstr)
        if event == 'hit':
            msg = self.tmp.format(player, 'Hit.', handstr)
        if event == 'stand':
            scores = [score for score in hand.score() if score <= 21]
            try:
                score = scores[-1]
            except IndexError:
                score = 'Bust.'
            msg = self.tmp.format(player, 'Stand.', score)
        print(msg)


# Command scripts.
def dealer_only():
    ui = UI()
    deck = cards.Deck.build(6)
    deck.shuffle()
    dealer = players.Dealer(name='Dealer')
    game.deal(deck, dealer, ui=ui)
    game.play(deck, dealer, ui=ui)
    ui.exit()


def one_player():
    ui = UI()
    deck = cards.Deck.build(6)
    deck.shuffle()
    dealer = players.Dealer(name='Dealer')
    player = players.Dealer(name='Player')
    game.deal(deck, dealer, (player,), ui=ui)
    ui.exit()    


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Blackjack')
    p.add_argument('-d', '--dealer_only', help='Just a dealer.', 
                   action='store_true')
    p.add_argument('-1', '--one_player', help='One player.', 
                   action='store_true')
    args = p.parse_args()
    
    if args.dealer_only:
        dealer_only()
    if args.one_player:
        one_player()
