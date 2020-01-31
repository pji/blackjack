"""
game
~~~~~

The module contains the main game loop for blackjack.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
from abc import ABC, abstractmethod
from json import dumps, loads
from typing import Union

from blackjack.cards import Deck, DeckObj, DOWN, Hand
from blackjack.model import Integer_, IsYes, valfactory
from blackjack.players import (Dealer, Player, make_player, restore_player, 
                               ValidPlayers, ValidPlayer)


# Internal utility functions.
def _build_hand(deck):
    """create the initial hand and deal a card into it."""
    card = deck.draw()
    card.flip()
    return Hand([card,])
    

# UI classes.
class EngineUI(ABC):
    # General operation methods.
    @abstractmethod
    def end(self):
        """End the UI."""
    
    @abstractmethod
    def reset(self):
        """Restart the UI."""
    
    @abstractmethod
    def start(self):
        """Start the UI."""
    
    
    # Input methods.
    @abstractmethod
    def doubledown_prompt(self) -> IsYes:
        """Ask user if they want to double down."""    
    
    @abstractmethod
    def hit_prompt(self) -> IsYes:
        """Ask user if they want to hit."""    
    
    @abstractmethod
    def insure_prompt(self) -> IsYes:
        """Ask user if they want to insure."""    
    
    @abstractmethod
    def nextgame_prompt(self) -> IsYes:
        """Ask user if they want to play another round."""    
    
    @abstractmethod
    def split_prompt(self) -> IsYes:
        """Ask user if they want to split."""    
    
    
    # Update methods.
    @abstractmethod
    def bet(self, player, bet):
        """Player places initial bet."""
    
    @abstractmethod
    def cleanup(self):
        """Clean up after the round ends."""
    
    @abstractmethod
    def deal(self, player, hand):
        """Player receives initial hand."""
    
    @abstractmethod
    def doubledown(self, player, bet):
        """Player doubles down."""
    
    @abstractmethod
    def flip(self, player, hand):
        """Player flips a card."""
    
    @abstractmethod
    def hit(self, player, hand):
        """Player hits."""
    
    @abstractmethod
    def insures(self, player, bet):
        """Player insures their hand."""
    
    @abstractmethod
    def insurepay(self, player, bet):
        """Insurance is paid to player."""
    
    @abstractmethod
    def joins(self, player):
        """Player joins the game."""
    
    @abstractmethod
    def leaves(self, player):
        """Player leaves the game."""
    
    @abstractmethod
    def loses(self, player):
        """Player loses."""
    
    @abstractmethod
    def loses_split(self, player):
        """Player loses on their split hand."""
    
    @abstractmethod
    def shuffles(self, player):
        """The deck is shuffled."""
    
    @abstractmethod
    def splits(self, player, bet):
        """Player splits their hand."""
    
    @abstractmethod
    def stand(self, player, hand):
        """Player stands."""
    
    @abstractmethod
    def tie(self, player, bet):
        """Player ties."""
    
    @abstractmethod
    def ties_split(self, player, bet):
        """Player ties on their split hand."""
    
    @abstractmethod
    def wins(self, player, bet):
        """Player wins."""
    
    @abstractmethod
    def wins_split(self, player, bet):
        """Player wins on their split hand."""


class BaseUI(EngineUI):
    """A base class for UI classes. It demonstrates the UI API, and it 
    serves as a silent UI for use in testing.
    """
    # General operation methods.
    def end(self):
        """End the UI."""
        pass
    
    def reset(self):
        """Reset the UI."""
        pass
    
    def start(self):
        """Start the UI."""
        pass
    
    # Input methods.
    def doubledown_prompt(self) -> IsYes:
        """Ask user if they want to double down."""    
        return IsYes(True)
    
    def hit_prompt(self) -> IsYes:
        """Ask user if they want to hit."""    
        return IsYes(True)
    
    def insure_prompt(self) -> IsYes:
        """Ask user if they want to insure."""    
        return IsYes(True)
    
    def nextgame_prompt(self) -> IsYes:
        """Ask user if they want to play another round."""    
        return IsYes(True)
    
    def split_prompt(self) -> IsYes:
        """Ask user if they want to split."""    
        return IsYes(True)
    
    # Update methods.
    def bet(self, player, bet):
        """Player places initial bet."""
        pass
    
    def cleanup(self):
        """Clean up after the round ends."""
        pass
    
    def deal(self, player, hand):
        """Player receives initial hand."""
        pass
    
    def doubledown(self, player, bet):
        """Player doubles down."""
        pass
    
    def flip(self, player, hand):
        """Player flips a card."""
        pass
    
    def hit(self, player, hand):
        """Player hits."""            
        pass
    
    def insures(self, player, bet):
        """Player insures their hand."""
        pass
    
    def insurepay(self, player, bet):
        """Insurance is paid to player."""
        pass
    
    def joins(self, player):
        """Player joins the game."""
        pass
    
    def leaves(self, player):
        """Player leaves the game."""
        pass
    
    def loses(self, player):
        """Player loses."""
        pass
    
    def loses_split(self, player):
        """Player loses on their split hand."""
        pass
    
    def shuffles(self, player):
        """The deck is shuffled."""
        pass
    
    def splits(self, player, bet):
        """Player splits their hand."""
        pass
    
    def stand(self, player, hand):
        """Player stands."""
        pass
    
    def tie(self, player, bet):
        """Player ties."""
        pass
    
    def ties_split(self, player, bet):
        """Player ties on their split hand."""
        pass
    
    def wins(self, player, bet):
        """Player wins."""
        pass
    
    def wins_split(self, player, bet):
        """Player wins on their split hand."""
        pass


# Game validator functions.
def validate_ui(self, value):
    """Validate EngineUI objects."""
    if not isinstance(value, EngineUI):
        reason = 'not an EngineUI object'
        raise ValueError(self.msg.format(reason))
    return value


# Game validating descriptors.
ValidUI = valfactory('ValidUI', validate_ui, 'Invalid EngineUI ({}).')


# Game engine class.
class Engine:
    """A game engine for blackjack."""
    deck = DeckObj('deck')
    playerlist = ValidPlayers('playerlist')
    dealer = ValidPlayer('dealer')
    ui = ValidUI('ui')
    buyin = Integer_('buyin')
    
    def __init__(self, deck: Deck = None, dealer: Player = None, 
                 playerlist: tuple = None, ui: EngineUI = None, 
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
        
        self.seats = len(playerlist)
    
    def __repr__(self):
        cls = self.__class__
        return (f'{cls.__name__}[{self.deck!r}, {self.dealer}, '
                f'{self.playerlist}, {self.ui}, {self.buyin}')
    
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
        self.ui.hit(player, hand)
        self.ui.stand(player, hand)
    
    def _add_player(self, player):
        """Add a new player to the first empty seat in the game.
        
        :param player: The player to add to the game.
        :return: None.
        :rtype: None
        """
        playerlist = list(self.playerlist)
        index = playerlist.index(None)
        playerlist[index] = player
        self.playerlist = playerlist
    
    def _asdict(self):
        """Return the object serialized as a dictionary."""
        return {
            'class': self.__class__.__name__,
            'deck': self.deck,
            'dealer': self.dealer,
            'playerlist': self.playerlist,
            'buyin': self.buyin,
        }
    
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
    
    def _deserialize(self, s):
        """Given a serialized Engine object, set this object's 
        attributes to match the serialized object's.
        """
        serial = loads(s)
        if serial['class'] == self.__class__.__name__:
            self.deck = Deck.deserialize(serial['deck'])
            self.dealer = Dealer.deserialize(serial['dealer'])
            self.playerlist = [restore_player(player) 
                               for player in serial['playerlist']]
            self.buyin = serial['buyin']
    
    def _double_down(self, player: Player, hand: Hand) -> None:
        """Handle the double down decision on a hand.
        
        :param player: The player who owns the hand.
        :param hand: The hand to make the decision on.
        :return: None.
        :rtype: None.
        """
        scores = [score for score in hand.score() if score < 12 and score > 8]
        if (scores and not hand.is_blackjack()
                   and player.chips >= self.buyin
                   and player.will_double_down(hand, self)):
            hand.doubled_down = True
            player.chips -= self.buyin
            self.ui.doubledown(player, self.buyin)
    
    def _draw(self):
        """Draw a card from the game deck."""
        if not self.deck:
            deck = Deck.build(self.deck.size)
            deck.shuffle()
            if deck.size > 3:
                deck.random_cut()
            self.deck = deck
            self.ui.shuffles(self.dealer)
        return self.deck.draw()
    
    def _hit(self, player, hand=None):
        """Handle the player's hitting and standing."""
        while (not hand.is_bust() and not hand.is_blackjack() 
                                  and player.will_hit(hand, self)):
            card = self._draw()
            card.flip()
            hand.append(card)
            self.ui.hit(player, hand)
        self.ui.stand(player, hand)
    
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
                self.ui.insures(player, cost)
    
    def _remove_player(self, player: Player) -> None:
        """Remove a player from the game."""
        playerlist = list(self.playerlist)
        index = playerlist.index(player)
        playerlist[index] = None
        self.playerlist = playerlist
    
    def _split(self, hand: Hand, player: Player) -> None:
        """Handle the splitting decision on a hand.
                
        :param hand: The hand to determine whether to split.
        :param player: The player who owns the hand.
        :return: Whether the hand was split.
        :rtype: bool
        """
        if (hand[0].rank == hand[1].rank 
                and player.will_split(hand, self)
                and player.chips >= self.buyin):
            new_hand1 = Hand([hand[0],])
            new_hand2 = Hand([hand[1],])
            player.hands = (new_hand1, new_hand2)
            player.chips -= self.buyin
            self.ui.splits(player, 20)
            return True
        return False
    
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
            self.ui.deal(player, player.hands[0])
        self.dealer.hands[0].append(self._draw())
        self.ui.deal(self.dealer, self.dealer.hands[0])
    
    def end(self):
        """End a round of blackjack."""
        dhand = self.dealer.hands[0]
        for player in self.playerlist:
            # Handle insurance.
            if player.insured and dhand.is_blackjack():
                payout = player.insured * 2
                if payout:
                    player.chips += payout
                    self.ui.insurepay(player, payout)
            
            # Handle hands.
            for index in range(len(player.hands)):
                phand = player.hands[index]
                result = self._compare_score(dhand, phand)
                event = None
                mod = 0
                
                # Event modifiers.
                if len(player.hands) == 1:
                    if dhand.is_blackjack() and phand.is_blackjack():
                        event = self.ui.tie
                    elif dhand.is_blackjack():
                        event = self.ui.loses
                    elif phand.is_blackjack():
                        event = self.ui.wins
                    elif result == None:
                        event = self.ui.tie
                    elif result == True:
                        event = self.ui.wins
                    else:
                        event = self.ui.loses
                else:
                    if dhand.is_blackjack():
                        if index == 1:
                            event = self.ui.loses_split
                        else:
                            event = self.ui.loses
                    elif result == None:
                        if index == 1:
                            event = self.ui.ties_split
                        else:
                            event = self.ui.tie
                    elif result == True:
                        if index == 1:
                            event = self.ui.wins_split
                        else:
                            event = self.ui.wins
                    else:
                        if index == 1:
                            event = self.ui.loses_split
                        else:
                            event = self.ui.loses
                
                # Payout modifiers.
                if event == self.ui.wins or event == self.ui.wins_split:
                    if phand.is_blackjack() and len(player.hands) == 1:
                        mod = 2.5
                    elif phand.doubled_down:
                        mod = 4
                    else:
                        mod = 2
                elif event == self.ui.tie or event == self.ui.ties_split:
                    if phand.doubled_down:
                        mod = 2
                    else:
                        mod = 1
                
                payout = mod * self.buyin
                player.chips += payout
                if event == self.ui.loses or event == self.ui.loses_split:
                    event(player)
                else:
                    event(player, payout)
        
    def new_game(self):
        """Update the UI with the players at the start of the game."""
        self.ui.joins(self.dealer)
        for player in self.playerlist:
            self.ui.joins(player)
    
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
                self._ace_split_hit(player, hand)
            
            # Standard hit decision.
            else:
                self._hit(player, player.hands[0])
                
        # The dealer has to flip before they hit.
        hand = self.dealer.hands[0]
        for card in hand:
            if card.facing == DOWN:
                card.flip()
                self.ui.flip(self.dealer, hand)
        self._hit(self.dealer, self.dealer.hands[0])
    
    def restore(self, fname: str = 'save.json') -> None:
        """Restore the state of a saved Engine object."""
        with open(fname, 'r') as f:
            s = f.read()
        self._deserialize(s)
        self.ui.reset()
        self.new_game()
    
    def save(self, fname: str = 'save.json') -> None:
        """Save the state of the current game."""
        serial = self.serialize()
        with open(fname, 'w') as f:
            f.write(serial)
    
    def serialize(self):
        """Return the object serialized as a JSON string."""
        serial = self._asdict()
        serial['deck'] = serial['deck'].serialize()
        serial['dealer'] = serial['dealer'].serialize()
        serial['playerlist'] = [player.serialize() 
                                for player in serial['playerlist']]
        return dumps(serial)
    
    def start(self):
        """Start a round of blackjack."""
        for player in self.playerlist:
            if player.chips >= self.buyin and player.will_buyin(self):
                player.chips -= self.buyin
                self.ui.bet(player, self.buyin)
            else:
                self._remove_player(player)
                self.ui.leaves(player)
                player = make_player(bet=self.buyin)
                self._add_player(player)
                self.ui.joins(player)
                self.ui.bet(player, self.buyin)


# The main game loop for blackjack.
def main(engine: Engine, is_interactive: bool = True) -> None:
    """The main game loop for blackjack.
    
    :param engine: An instance of the blackjack Engine.
    :return: None.
    :rtype: None.
    """
    engine.ui.start(is_interactive=is_interactive)
    engine.new_game()
    play = yield True
    while play:
        engine.start()
        engine.deal()
        engine.play()
        engine.end()
        play = yield engine.ui.nextgame_prompt().value
        engine.ui.cleanup()
    engine.ui.end()
