"""
game
~~~~~

The module contains the main game loop for blackjack.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from typing import Union

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
    
    def input(self, event, detail=None, default=None):
        return default
    
    def update(self, event, player, detail):
        pass


class Game:
    """A game of blackjack."""
    def __init__(self, deck: Deck = None, dealer: Player = None, 
                 playerlist: tuple = None, ui: BaseUI = None, 
                 buyin: float = 0) -> None:
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
        
        self.buyin = buyin
    
    def __repr__(self):
        cls = self.__class__
        return (f'{cls.__name__}[{self.deck!r}, {self.dealer}, {self.playlist},'
                f'{ui}, {buyin}')
    
    def start(self):
        """Start a round of blackjack."""
        for player in self.playerlist:
            if player.chips >= self.buyin:
                player.chips -= self.buyin
                self.ui.update('buyin', player, [self.buyin, player.chips])
            else:
                self._remove_player(player)
                self.ui.update('remove', player, '')
    
    def end(self):
        """End a round of blackjack."""
        dhand = self.dealer.hands[0]
        for player in self.playerlist:
            event = 'payout'
            if player.insured and dhand.is_blackjack():
                payout = player.insured * 2
                if payout:
                    player.chips += payout
                    self.ui.update('insurepay', player, [payout, player.chips])
            for phand in player.hands:
                payout = 0
                result = self._compare_score(dhand, phand)
                if (result == True 
                        and phand.is_blackjack() 
                        and len(player.hands) == 2):
                    payout = 2 * self.buyin
                elif result == True and phand.is_blackjack():
                    payout = 2.5 * self.buyin
                elif result == True and phand.doubled_down:
                    payout = 4 * self.buyin
                elif result == True:
                    payout = 2 * self.buyin
                elif result == None and dhand.is_blackjack():
                    pass
                elif result == None:
                    event = 'tie'
                    payout = self.buyin
                if payout:
                    player.chips += payout
                    self.ui.update(event, player, [payout, player.chips])
    
    def deal(self):
        """Deal a round of blackjack."""
        # First card.
        for player in self.playerlist:
            player.hands = (self._build_hand(),)
        self.dealer.hands = (self._build_hand(),)
        
        # Second card.
        for player in self.playerlist:
            card = self._draw()
            card.flip()
            player.hands[0].append(card)
            self.ui.update('deal', player, player.hands[0])
        self.dealer.hands[0].append(self._draw())
        self.ui.update('deal', self.dealer, self.dealer.hands[0])
    
    def play(self):
        """Play a round of blackjack."""
        # Handle the players.
        for player in self.playerlist:
            # Insurance decision.
            self._insure(player)
            
            # Split decision.
            if self._split(player.hands[0], player):
                for hand in player.hands:
                    if hand[0].rank == 1:
                        self._ace_split_hit(player, hand)
                    else:
                        self._hit(player, hand)
            
            # Double down decision.
            elif self._double_down(player, player.hands[0]):
                self._ace_plit_hit(player, hand)
            
            # Standard hit decision.
            else:
                self._hit(player)
        
        # Insurance decision.
        
        # The dealer has to flip before they hit.
        hand = self.dealer.hands[0]
        for card in hand:
            if card.facing == DOWN:
                card.flip()
                self.ui.update('flip', self.dealer, hand)
        self._hit(self.dealer)
    
    def _ace_split_hit(self, player: Player, hand: Hand) -> None:
        """Handle a hand made by splitting a pair of aces. It also 
        handles hands hit after doubling down.
        
        :param player: The player who owns the hand.
        :param hand: The hand to hit.
        :return: None.
        :rtype: None.
        """
        card = self._draw()
        card.flip()
        hand.append(card)
        self.ui.update('hit', player, hand)
        self.ui.update('stand', player, hand)
    
    def _build_hand(self):
        """create the initial hand and deal a card into it."""
        card = self._draw()
        card.flip()
        return Hand([card,])

    def _compare_score(self, d_hand: Hand, p_hand: Hand) -> Union[None, bool]:
        """Determine if the player's hand won.
        
        :param d_hand: The dealer's hand.
        :param p_hand: The player's hand.
        :return: True if the player wins, False if the dealer wins, 
            and None if it's a tie.
        :rtype: None, bool
        """
        def filter_scores(hand):
            return [score for score in hand.score() if score <= 21]
        
        try:
            p_score = filter_scores(p_hand)[-1]
        except IndexError:
            return False
        try:
            d_score = filter_scores(d_hand)[-1]
        except IndexError:
            return True
        if p_score > d_score:
            return True
        if p_score < d_score:
            return False
        return None
    
    def _double_down(self, player: Player, hand: Hand) -> None:
        """Handle the double down decision on a hand.
        
        :param player: The player who owns the hand.
        :param hand: The hand to make the decision on.
        :return: None.
        :rtype: None.
        """
        scores = [score for score in hand.score() if score < 12 and score > 8]
        if (scores and player.will_double_down(hand, self) 
                   and player.chips >= self.buyin
                   and not hand.is_blackjack()):
            hand.doubled_down = True
            player.chips -= self.buyin
            self.ui.update('doubled', player, [self.buyin, player.chips])
    
    def _draw(self):
        """Draw a card from the game deck."""
        if not self.deck:
            deck = Deck.build(self.deck.size)
            deck.shuffle()
            if deck.size > 3:
                deck.random_cut()
            self.deck = deck
            self.ui.update('shuffled', self.dealer, '')
        return self.deck.draw()
    
    def _hit(self, player, hand=None):
        """Handle the player's hitting and standing."""
        if not hand:
            hand = player.hands[0]
        while player.will_hit(hand, self):
            card = self._draw()
            card.flip()
            hand.append(card)
            self.ui.update('hit', player, hand)
        self.ui.update('stand', player, hand)

    def _insure(self, player: Player) -> None:
        """Handle the insurance decision for a player.
        
        :param player: The player who can insure.
        :return: None.
        :rtype: None.
        """
        if self.dealer.hands[0][0].rank == 1:
            cost = player.will_insure(self)
            if cost:
                if cost > player.chips:
                    cost = player.chips
                if cost > self.buyin / 2:
                    cost = self.buyin / 2
                player.insured = cost
                player.chips -= cost
                self.ui.update('insured', player, [cost, player.chips])
    
    def _remove_player(self, player: Player) -> None:
        """Remove a player from the game."""
        playerlist = list(self.playerlist)
        playerlist.remove(player)
        self.playerlist = playerlist
    
    def _split(self, hand: Hand, player: Player) -> None:
        """Handle the splitting decision on a hand.
                
        :param hand: The hand to determine whether to split.
        :param player: The player who owns the hand.
        :return: Whether the hand was split.
        :rtype: bool
        """
        if hand[0].rank == hand[1].rank and player.will_split(hand, self):
            new_hand1 = Hand([hand[0],])
            new_hand2 = Hand([hand[1],])
            player.hands = (new_hand1, new_hand2)
            self.ui.update('split', player, player.hands)
            return True
        return False