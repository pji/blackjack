"""
game
~~~~~

The module contains the main game loop for blackjack.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from blackjack.cards import Deck, DOWN, Hand
from blackjack.players import Dealer, Player


# Internal utility functions.
def _build_hand(deck):
    """create the initial hand and deal a card into it."""
    card = deck.draw()
    card.flip()
    return Hand([card,])
    

# Public classes.
class BaseUI:
    """A base class for UI classes. It demonstrates the UI API, and it 
    serves as a silent UI for use in testing.
    """
    def enter(self):
        pass
    
    def exit(self):
        pass
    
    def update(self, event, player, hand):
        pass


class Game:
    """A game of blackjack."""
    def __init__(self, casino:bool, dealer: Player = None, 
                 ui: BaseUI = None) -> None:
        """Initialize and instance of the class.
        
        :param casino: Whether the game is using a casino deck.
        :return: None.
        :rtype: None.
        """
        self.casino = casino
        if casino:
            self.deck = Deck.build(6)
        else:
            self.deck = Deck.build()
        
        if not dealer:
            dealer = Dealer(name='Dealer')
        self.dealer = dealer
        
        if not ui:
            ui = BaseUI()
        self.ui = ui
    
    def deal(self):
        """Deal a round of blackjack."""
        self.dealer.hands = (_build_hand(self.deck),)
        self.dealer.hands[0].append(self.deck.draw())
        self.ui.update('deal', self.dealer, self.dealer.hands[0])


# Public functions.
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
    if not players:
        players = []
    
    # First handle each player.
    for player in players:
        hand = player.hands[0]
        while player.will_hit(hand):
            card = deck.draw()
            card.flip()
            hand.append(card)
            if ui:
                ui.update('hit', player, hand)
        if ui:
            ui.update('stand', player, hand)
    
    # Then handle the dealer.
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


def split(player:Player, hand:Hand) -> None:
    """If the given hand can be split and the player wants to split, 
    split the player's hand.
    
    :param player: The player whose hand may be able to be split.
    :param hand: The hand that may be able to be split.
    :return: None.
    :rtype: None.
    """
    pass