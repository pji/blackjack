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
    def __init__(self, deck: Deck = None, dealer: Player = None, 
                 playerlist: tuple = None, ui: BaseUI = None) -> None:
        """Initialize and instance of the class.
        
        :param casino: Whether the game is using a casino deck.
        :param dealer: The dealer for the game.
        :param playerlist: A tuple containing the players in the game.
        :param ui: The user interface for the game.
        :return: None.
        :rtype: None.
        """
        if not deck:
            deck = Deck.build(6)
        self.deck = deck
        
        if not playerlist:
            playerlist = ()
        self.playerlist = playerlist
        
        if not dealer:
            dealer = Dealer(name='Dealer')
        self.dealer = dealer
        
        if not ui:
            ui = BaseUI()
        self.ui = ui
    
    def deal(self):
        """Deal a round of blackjack."""
        # First card.
        for player in self.playerlist:
            player.hands = (_build_hand(self.deck),)
        self.dealer.hands = (_build_hand(self.deck),)
        
        # Second card.
        for player in self.playerlist:
            card = self.deck.draw()
            card.flip()
            player.hands[0].append(card)
            self.ui.update('deal', player, player.hands[0])
        self.dealer.hands[0].append(self.deck.draw())
        self.ui.update('deal', self.dealer, self.dealer.hands[0])
    
    def play(self):
        """Play a round of blackjack.
        
        Does not handle split aces properly.
        """
        # First handle the players.
        def hit(player):
            """Handle the player's hitting and standing."""
            hand = player.hands[0]
            while player.will_hit(hand):
                card = self.deck.draw()
                card.flip()
                hand.append(card)
                self.ui.update('hit', player, hand)
            self.ui.update('stand', player, hand)
        
        # Handle the players.
        for player in self.playerlist:
            hit(player)
        
        # The dealer has to flip before they hit.
        hand = self.dealer.hands[0]
        for card in hand:
            if card.facing == DOWN:
                card.flip()
                self.ui.update('flip', self.dealer, hand)
        hit(self.dealer)
    
    def _split(self, hand: Hand, player: Player) -> None:
        """Handle the splitting decision on a hand.
                
        :param hand: The hand to determine whether to split.
        :param player: The player who owns the hand.
        :return: Whether the hand was split.
        :rtype: bool
        """
        if hand[0].rank == hand[1].rank and player.will_split(hand):
            new_hand1 = Hand([hand[0],])
            new_hand2 = Hand([hand[1],])
            player.hands = (new_hand1, new_hand2)
            self.ui.update('split', player, player.hands)
            return True
        return False
                
