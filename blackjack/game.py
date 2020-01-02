"""
game
~~~~~

The module contains the main game loop for blackjack.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from blackjack.cards import Deck, Hand
from blackjack.players import Player


def deal(deck: Deck, dealer: Player, players: list = None) -> None:
    """Perform the initial deal of a blackjack game."""
    card = deck.draw()
    card.flip()
    hand = Hand([card,])
    dealer.hands = [hand,]
    
    card = deck.draw()
    hand.append(card)

def play(deck: Deck, dealer: Player, players: list = None) -> None:
    """Perform the play phase of a blackjack game."""
    hand = dealer.hands[0]
    while dealer.will_hit(hand):
        card = deck.draw()
        hand.append(card)