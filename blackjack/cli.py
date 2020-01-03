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
    def update(self, event:str, player:str, hand:cards.Hand) -> None:
        """Update the UI.
        
        :param event: The event the UI needs to display.
        :param player: The player name involved in the event.
        :param hand: The hand to display.
        :return: None.
        :rtype: None.
        """
        msg = None
        if event == 'deal':
            msg = f'{player} was dealt {hand[0]} {hand[1]}.'
        if event == 'hit':
            handstr = ' '.join([str(card) for card in hand])
            msg = f'{player} hits. Hand now {handstr}.'
        print(msg)


# Command scripts.
def dealer_only():
    ui = UI()
    deck = cards.Deck.build(6)
    deck.shuffle()
    dealer = players.Player()
    dealer.will_hit = partial(players.dealer_will_hit, None)
    game.deal(deck, dealer, ui=ui)
#     for card in dealer.hands[0]:
#         print(card, end=' ')
#     print()
    for card in dealer.hands[0]:
        if card.facing == cards.DOWN:
            card.flip()
    game.play(deck, dealer, ui=ui)
    print()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Blackjack')
    p.add_argument('-d', '--dealer_only', help='Just a dealer.', 
                   action='store_true')
    args = p.parse_args()
    
    if args.dealer_only:
        dealer_only()
