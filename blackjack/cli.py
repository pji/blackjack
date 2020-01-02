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


# Command scripts.
def dealer_only():
    deck = cards.Deck.build(6)
    deck.shuffle()
    dealer = players.Player()
    dealer.will_hit = partial(players.dealer_will_hit, None)
    game.deal(deck, dealer)
    for card in dealer.hands[0]:
        print(card, end=' ')
    print()
    game.play(deck, dealer)
    for card in dealer.hands[0]:
        if card.facing == cards.DOWN:
            card.flip()
        print(card, end=' ')
    print()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Blackjack')
    p.add_argument('-d', '--dealer_only', help='Just a dealer.', 
                   action='store_true')
    args = p.parse_args()
    
    if args.dealer_only:
        dealer_only()
