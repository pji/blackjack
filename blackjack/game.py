"""
game
~~~~~

The module contains the main game loop for blackjack.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from blackjack.cards import Deck, DOWN, Hand
from blackjack.players import Player


def _build_hand(deck):
    """create the initial hand and deal a card into it."""
    card = deck.draw()
    card.flip()
    return Hand([card,])
    

def deal(deck: Deck, dealer: Player, players: list = None, ui = None) -> None:
    """Perform the initial deal of a blackjack game."""
    if not players:
        players = []
    
    # First card to players then dealer.
    for player in players:
        player.hands = (_build_hand(deck),)
    dealer.hands = (_build_hand(deck),)
    
    # Second card to players, then face down to dealer.
    for player in players:
        card = deck.draw()
        card.flip()
        player.hands[0].append(card)
        if ui:
            ui.update('deal', player, player.hands[0])
    dealer.hands[0].append(deck.draw())
    if ui:
        ui.update('deal', dealer, dealer.hands[0])

def play(deck: Deck, dealer: Player, players: list = None, ui = None) -> None:
    """Perform the play phase of a blackjack game."""
    hand = dealer.hands[0]
    for card in hand:
        if card.facing == DOWN:
            card.flip()
            if ui:
                ui.update('flip', dealer, hand)
    while dealer.will_hit(hand):
        card = deck.draw()
        card.flip()
        hand.append(card)
        if ui:
            ui.update('hit', dealer, hand)
    if ui:
        ui.update('stand', dealer, hand)