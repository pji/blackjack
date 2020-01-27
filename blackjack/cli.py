"""
cli
~~~

The module contains the basic classes used by blackjack for handling 
a command line interface.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import argparse
from collections import namedtuple
from time import sleep
import traceback as tb
from typing import Any, Sequence

from blessed import Terminal

from blackjack import cards, game, model, players, termui


# UI objects.
class LogUI(game.BaseUI):
    tmp = '{:<15} {:<15} {:<}'
    
    def __init__(self, silent: bool = False) -> None:
        self.is_interactive = silent
    
    # Engine UI protocol.
    def end(self, is_interactive: bool = True) -> None:
        """Print the initial banners for the game.
        
        :param is_interactive: Whether the session is viewed by a 
            player.
        :return: None.
        :rtype: NoneType
        """
        self.is_interactive = is_interactive
        if self.is_interactive:
            print('\u2500' * 50)
            print()
    
    def start(self, is_interactive: bool = True) -> None:
        """Print the initial banners for the game.
        
        :param is_interactive: Whether the session is viewed by a 
            player.
        :return: None.
        :rtype: NoneType
        """
        self.is_interactive = is_interactive
        if self.is_interactive:
            print()
            print('BLACKJACK!')
            print()
            print(self.tmp.format('Player', 'Action', 'Hand'))
            print('\u2500' * 50)
    
    # Update methods.
    def _update_bet(self, player:players.Player, bet:int,
                     event:str) -> None:
        """Report that a hand has changed.
        
        :param player: The player who owns the hand.
        :param bet: The amount of the bet that changed.
        :param event: The specific event to report.
        :return: None.
        :rtype: NoneType
        """
        fmt = f'{bet} ({player.chips})'
        self._update_event(player, event, fmt)
    
    def _update_event(self, player:players.Player, event:str, 
                      detail: Any = '') -> None:
        """Report that an event has occurred.
        
        :param player: The player who owns the hand.
        :param event: The specific event to report.
        :param detail: A relevant detail about the event that can be 
            coerced into a string.
        :return: None.
        :rtype: NoneType
        """
        print(self.tmp.format(player, event, detail))
    
    def _update_hand(self, player:players.Player, hand:cards.Hand,
                     event:str) -> None:
        """Report that a hand has changed.
        
        :param player: The player who owns the hand.
        :param hand: The hand that changed.
        :param event: The specific event to report.
        :return: None.
        :rtype: NoneType
        """
        self._update_event(player, event, hand)
    
    def bet(self, player, bet):
        """Player places initial bet."""
        self._update_bet(player, bet, 'Bet.')
    
    def cleanup(self):
        """Clean up after the round ends."""
        self.end()
        self.start()
    
    def deal(self, player, hand):
        """Player receives initial hand."""
        self._update_hand(player, hand, 'Dealt hand.')
    
    def doubledown(self, player, bet):
        """Player doubles down."""
        self._update_bet(player, bet, 'Double down.')
    
    def flip(self, player, hand):
        """Player flips a card."""
        self._update_hand(player, hand, 'Flip.')
    
    def hit(self, player, hand):
        """Player hits."""            
        self._update_hand(player, hand, 'Hit.')
    
    def insures(self, player, bet):
        """Player insures their hand."""
        self._update_bet(player, bet, 'Insures.')
    
    def insurepay(self, player, bet):
        """Insurance is paid to player."""
        self._update_bet(player, bet, 'Insure pay.')
    
    def joins(self, player):
        """Player joins the game."""
        self._update_event(player, 'Joins.')
    
    def leaves(self, player):
        """Player leaves the game."""
        self._update_event(player, 'Leaves.')
    
    def loses(self, player):
        """Player loses."""
        self._update_bet(player, '', 'Loses.')
    
    def loses_split(self, player):
        """Player loses on their split hand."""
        self.loses(player)
    
    def shuffles(self, player):
        """The deck is shuffled."""
        self._update_event(player, 'Shuffles.')
    
    def splits(self, player, bet):
        """Player splits their hand."""
        self._update_bet(player, bet, 'Splits.')
    
    def stand(self, player, hand):
        """Player stands."""
        self._update_hand(player, hand, 'Stand.')
    
    def tie(self, player, bet):
        """Player ties."""
        self._update_bet(player, bet, 'Tie.')
    
    def ties_split(self, player, bet):
        """Player ties on their split hand."""
        self.tie(player, bet)
    
    def wins(self, player, bet):
        """Player wins."""
        self._update_bet(player, bet, 'Wins.')
    
    def wins_split(self, player, bet):
        """Player wins on their split hand."""
        self.wins(player, bet)
    
    
    # Input methods.
    def _yesno_prompt(self, prompt:str, default: bool = True) -> model.IsYes:
        """Prompt the user for a yes/no answer."""
        response = None
        fmt = '{} [yn] > '
        
        # Repeat the prompt until you get a valid response.
        while not response:
            untrusted = input(fmt.format(prompt))
            
            # Allow the response to default to true. Saves typing when 
            # playing. 
            if not untrusted:
                untrusted = default
            
            # Determine if the input is valid.
            try:
                response = model.IsYes(untrusted)
            
            # If it's not valid, the ValueError will be caught, 
            # response won't be set, so the prompt will be repeated.
            except ValueError:
                pass
        
        return response
        
    def doubledown_prompt(self) -> model.IsYes:
        """Ask user if they want to double down."""    
        return self._yesno_prompt('Double down?', 'y')
    
    def hit_prompt(self) -> model.IsYes:
        """Ask user if they want to hit."""    
        return self._yesno_prompt('Hit?', 'y')
    
    def insure_prompt(self) -> model.IsYes:
        """Ask user if they want to insure."""    
        return self._yesno_prompt('Insure?', 'y')
    
    def nextgame_prompt(self) -> model.IsYes:
        """Ask user if they want to play another round."""    
        return self._yesno_prompt('Next game?', 'y')
    
    def split_prompt(self) -> model.IsYes:
        """Ask user if they want to split."""    
        return self._yesno_prompt('Split?', 'y')


class TableUI(game.EngineUI):
    """A table-based terminal UI for blackjack."""
    # General operation methods.
    def __init__(self, ctlr: termui.TerminalController = None, 
                 seats: int = 1) -> None:
        """Initialize and instance of the class.
        
        :param ctlr: (Optional.) The TerminalController object running 
            the UI.
        :param seats: (Optional.) The number of seats that will be 
            available for the game.
        """
        self.seats = seats
        if not ctlr:
            ctlr = self._make_ctlr()
        self.ctlr = ctlr
        self.loop = None
    
    def _make_ctlr(self):
        """Returns a termui.Table object for blackjack."""
        fields = (
            ('Player', '{:<14}'),
            ('Chips', '{:>7}'),
            ('Bet', '{:>3}'),
            ('Hand', '{:<27}'),
            ('Event', '{:<23}'),
        )
        return termui.Table('Blackjack', fields, rows=self.seats)
    
    def end(self):
        """End the UI loop gracefully."""
        self.loop.close()
    
    def start(self, is_interactive=False):
        """Start the UI."""
        self.loop = termui.main(self.ctlr, is_interactive)
        next(self.loop)
        self.loop.send(('draw',))
    
    
    # Input methods.
    def _prompt(self, prompt, default):
        """Prompt for a response from the user."""
        return self.loop.send(('input', prompt, default))
    
    def _yesno_prompt(self, prompt, default):
        prompt = f'{prompt} [yn] > '
        valid = None
        while not valid:
            resp = self._prompt(prompt, default)
            try:
                valid = model.IsYes(resp)
            except ValueError:
                pass
        return valid
    
    def doubledown_prompt(self) -> model.IsYes:
        """Ask user if they want to double down."""
        prompt = 'Double down?'
        default = 'y'
        return self._yesno_prompt(prompt, default)
    
    def hit_prompt(self) -> model.IsYes:
        """Ask user if they want to hit."""
        prompt = 'Hit?'
        default = 'y'
        return self._yesno_prompt(prompt, default)
    
    def insure_prompt(self) -> model.IsYes:
        """Ask user if they want to insure."""
        prompt = 'Buy insurance?'
        default = 'y'
        return self._yesno_prompt(prompt, default)
    
    def nextgame_prompt(self) -> model.IsYes:
        """Ask user if they want to play another round."""
        prompt = 'Play another round?'
        default = 'y'
        return self._yesno_prompt(prompt, default)
    
    def split_prompt(self) -> model.IsYes:
        """Ask user if they want to split."""
        prompt = 'Split your hand?'
        default = 'y'
        return self._yesno_prompt(prompt, default)

    
    # Update methods.
    def _get_field_index(self, needed: Sequence[str]) -> list:
        """Get the indices the given fields of the data table.
        
        :param needed: The names of the fields you need the indexes 
            for.
        :return: A list of the indices.
        :rtype: list
        """
        fields = [field.name for field in self.ctlr.fields]
        return [fields.index(field) for field in needed]
    
    def _get_player_row_and_data(self, player: players.Player) -> tuple:
        """Get the data table row for the given player.
        
        :param player: The player to get the row for.
        :return: An index and a copy of the data table.
        :rtype: tuple
        """
        # Get the player's row to update.
        # Since termui.Table determines which fields to updata by 
        # looking for changes in the data table, it's very important 
        # that we create a copy of data here.
        data = [row[:] for row in self.ctlr.data]
        playerlist = [row[0] for row in data]
        row = playerlist.index(player)
        return row, data
    
    def _update_bet(self, player, bet, event, split=False):
        """The player's bet and chips information needs to be 
        updated.
        
        :param player: The player whose row to update.
        :param bet: The player's bet.
        :param event: The event that occurred.
        :param split: Whether the update is for the split hand.
        :return: None.
        :rtype: NoneType
        """
        row, data = self._get_player_row_and_data(player)
        if split and len(player.hands) == 2:
            row += 1
        
        affected_fields = ('Chips', 'Bet', 'Event')
        i_chips, i_bet, i_event = self._get_field_index(affected_fields)
        
        if not split:
            data[row][i_chips] = player.chips
        data[row][i_bet] = bet
        data[row][i_event] = event
        self.loop.send(('update', data))
    
    def _update_event(self, player, event):
        """The player's event information needs to be updated.
        """
        row, data = self._get_player_row_and_data(player)
        
        affected_fields = ('Event',)
        i_event, = self._get_field_index(affected_fields)
        
        data[row][i_event] = event
        self.loop.send(('update', data))
    
    def _update_hand(self, player, hand, event):
        """The player's hand information needs to be updated."""
        row, data = self._get_player_row_and_data(player)
        if len(player.hands) == 2:
            if player.hands.index(hand) == 1:
                row += 1
        
        affected_fields = ('Hand', 'Event')
        i_hand, i_event = self._get_field_index(affected_fields)
        
        data[row][i_hand] = str(hand)
        data[row][i_event] = event
        self.loop.send(('update', data))
    
    def bet(self, player, bet):
        """Player places initial bet."""
        self._update_bet(player, bet, 'Bets.')
    
    def cleanup(self):
        """Clean up information from the previous round."""
        data = [row[:] for row in self.ctlr.data]
        affected = ['Player', 'Chips', 'Bet', 'Hand', 'Event']
        i_play, i_chp, i_bet, i_hand, i_event = self._get_field_index(affected)
        data = [row for row in data if isinstance(row[i_play], players.Player)]
        for row in data:
            row[i_chp] = row[i_play].chips
            row[i_bet] = ''
            row[i_hand] = ''
            row[i_event] = ''
        self.loop.send(('update', data))
    
    def deal(self, player, hand):
        """Player recieves initial hand."""
        self._update_hand(player, hand, 'Takes hand.')
    
    def doubledown(self, player, bet):
        """Player doubles down."""
        self._update_bet(player, bet, 'Doubles down.')
    
    def flip(self, player, hand):
        """Player flips a card."""
        self._update_hand(player, hand, 'Flips card.')
    
    def hit(self, player, hand):
        """Player hits."""
        self._update_hand(player, hand, 'Hits.')
    
    def insures(self, player, bet):
        """Player insures their hand."""
        self._update_bet(player, bet, f'Buys {bet} insurance.')
    
    def insurepay(self, player, bet):
        """Insurance is paid to player."""
        self._update_bet(player, bet, f'Insurance pays {bet}.')
    
    def joins(self, player):
        """Player joins the game.
        
        :param player: The player to add to the game.
        :return: None.
        :rtype: NoneType.
        """
        row, data = self._get_player_row_and_data('')
        affected = ['Player', 'Chips', 'Event']
        i_play, i_chip, i_event = self._get_field_index(affected)
        
        data[row][i_play] = player
        data[row][i_chip] = player.chips
        data[row][i_event] = 'Sits down.'
        
        self.loop.send(('update', data))
    
    def leaves(self, player):
        """Player leaves the game.
        
        :param player: The player to remove from the game.
        :return: None.
        :rtype: NoneType.
        """
        row, data = self._get_player_row_and_data(player)
        affected = ['Player', 'Chips', 'Bet', 'Hand', 'Event']
        i_play, i_chip, i_bet, i_hand, i_event = self._get_field_index(affected)
        
        # Send leaving message to UI.
        data[row][i_chip] = ''
        data[row][i_bet] = ''
        data[row][i_hand] = ''
        data[row][i_event] = 'Walks away.'
        self.loop.send(('update', data))
        
        # Remove the player from the data table.
        self.ctlr.data[row][i_play] = ''
    
    def loses(self, player):
        """Player loses."""
        self._update_bet(player, '', 'Loses.')
    
    def loses_split(self, player):
        """Player loses on their split hand."""
        self._update_bet(player, '', 'Loses.', True)
    
    def shuffles(self, player):
        """The deck is shuffled."""
        self._update_event(player, 'Shuffles the deck.')
    
    def splits(self, player, bet):
        """Player splits their hand."""
        row, data = self._get_player_row_and_data(player)
        affected = ['Player', 'Chips', 'Bet', 'Hand', 'Event']
        i_play, i_chip, i_bet, i_hand, i_event = self._get_field_index(affected)
        
        # Update existing row.
        data[row][i_chip] = player.chips
        data[row][i_bet] = bet
        data[row][i_hand] = str(player.hands[0])
        data[row][i_event] = 'Splits hand.'
        
        # Build the new split row and add it.
        new_row = ['' for field in range(len(self.ctlr.fields))]
        new_row[i_play] = '  \u2514\u2500'
        new_row[i_bet] = bet
        new_row[i_hand] = str(player.hands[1])
        data.insert(row + 1, new_row)
        
        self.loop.send(('update', data))
    
    def stand(self, player, hand):
        """Player stands."""
        self._update_hand(player, hand, 'Stands.')
    
    def tie(self, player, bet):
        """Player ties."""
        self._update_bet(player, '', f'Ties {bet}.')
    
    def ties_split(self, player, bet):
        """Player ties."""
        self._update_bet(player, '', f'Ties {bet}.', True)
    
    def wins(self, player, bet):
        """Player wins."""
        self._update_bet(player, '', f'Wins {bet}.')
    
    def wins_split(self, player, bet):
        """Player wins on their split hand."""
        self._update_bet(player, '', f'Wins {bet}.', True)


# Command scripts.
def dealer_only():
    ui = LogUI()
    g = game.Engine(ui=ui)
    g.deck.shuffle()
    ui.start()
    g.deal()
    g.play()
    ui.end()


def one_player():
    ui = LogUI()
    play = True
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    player = players.AutoPlayer(name='Player', chips=200)
    g = game.Engine(deck, dealer, (player,), ui=ui, buyin=2)
    while play:
        ui.start()
        g.start()
        g.deal()
        g.play()
        g.end()
        ui.end()
        play = ui.nextgame_prompt().value


def two_player():
    p1 = players.AutoPlayer(name='John', chips=200)
    p2 = players.BetterPlayer(name='Michael', chips=200)
    ui = LogUI()
    play = True
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    g = game.Engine(deck, dealer, (p1, p2,), ui=ui, buyin=2)
    while play:
        ui.start()
        g.start()
        g.deal()
        g.play()
        g.end()
        ui.end()
        play = ui.nextgame_prompt().value


def three_player():
    p1 = players.AutoPlayer(name='John', chips=200)
    p2 = players.BetterPlayer(name='Michael', chips=200)
    p3 = players.UserPlayer(name='You', chips=200)
    ui = LogUI()
    play = True
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    g = game.Engine(deck, dealer, (p1, p2, p3,), ui=ui, buyin=2)
    while play:
        ui.start()
        g.start()
        g.deal()
        g.play()
        g.end()
        ui.end()
        play = ui.nextgame_prompt().value


def four_player():
    playerlist = []
    for index in range(4):
        playerlist.append(players.make_player())
    ui = LogUI()
    play = True
    deck = cards.Deck.build(6)
    deck.shuffle()
    deck.random_cut()
    dealer = players.Dealer(name='Dealer')
    g = game.Engine(deck, dealer, playerlist, ui=ui, buyin=2)
    while play:
        ui.start()
        g.start()
        g.deal()
        g.play()
        g.end()
        ui.end()
        play = ui.nextgame_prompt().value


def dui():
    try:
        ui = TableUI(seats=6)
        deck = cards.Deck.build(6)
        deck.shuffle()
        deck.random_cut()
        dealer = players.Dealer(name='Dealer')
        playerlist = []
        for index in range(4):
            playerlist.append(players.make_player(bet=20))
        playerlist.append(players.UserPlayer(name='You', chips=200))
        g = game.Engine(deck, dealer, playerlist, ui=ui, buyin=20)
        ui.start(True)
        g.new_game()
        play = True
        while play:
                g.start()
                g.deal()
                g.play()
                g.end()
                play = ui.nextgame_prompt().value
                if play:
                    ui.cleanup()
    except Exception as ex:
        with open('exception.log', 'w') as fh:
            fh.write(str(ex.args))
            tb_str = ''.join(tb.format_tb(ex.__traceback__))
            fh.write(tb_str)
        raise ex


def test():
    player = players.make_player()
    print(player.asdict())

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Blackjack')
    p.add_argument('-d', '--dealer_only', help='Just a dealer game.', 
                   action='store_true')
    p.add_argument('-1', '--one_player', help='One player game.', 
                   action='store_true')
    p.add_argument('-2', '--two_player', help='Two player game.', 
                   action='store_true')
    p.add_argument('-3', '--three_player', help='Three player game.', 
                   action='store_true')
    p.add_argument('-4', '--four_player', help='Four player game.', 
                   action='store_true')
    p.add_argument('-D', '--dui', help='Dynamic UI game.', 
                   action='store_true')
    p.add_argument('-p', '--players', help='Number of random players.', 
                   action='store', type=int)
    p.add_argument('-u', '--user', help='Add a human player.', 
                   action='store_true')
    p.add_argument('-c', '--chips', help='Number of starting chips.', 
                   action='store', type=int, default=200)
    p.add_argument('-C', '--cost', help='Hand bet amount.', 
                   action='store', type=int, default=20)
    p.add_argument('-t', '--test', help='Run current test.', 
                   action='store_true')
    args = p.parse_args()
    
    if args.dealer_only:
        dealer_only()
    elif args.one_player:
        one_player()
    elif args.two_player:
        two_player()
    elif args.three_player:
        three_player()
    elif args.four_player:
        four_player()
    elif args.dui:
        dui()
    elif args.test:
        test()
    else:
        if args.chips > 9999999:
            reason = 'Cannot start with more than 9999999 chips.'
            raise ValueError(reason)
        if args.cost > 99999999:
            reason = 'Bets cannot be more than 99999999.'
            raise ValueError(reason)
        
        playerlist = []
        for _ in range(int(args.players)):
            playerlist.append(players.make_player(args.chips))
        if args.user:
            playerlist.append(players.UserPlayer(name='You', chips=args.chips))
        
        deck = cards.Deck.build(6)
        deck.shuffle()
        deck.random_cut()
        ui = TableUI(seats=len(playerlist) + 1)
        g = game.Engine(deck, None, playerlist, ui, args.cost)
        ui.start(True)
        g.new_game()
        
        play_again = True
        while play_again:
            try:
                g.start()
                g.deal()
                g.play()
                g.end()
                play_again = ui.nextgame_prompt().value
                if play_again:
                    ui.cleanup()
            except Exception as ex:
                with open('exception.log', 'w') as fh:
                    fh.write(str(ex.args))
                    tb_str = ''.join(tb.format_tb(ex.__traceback__))
                    fh.write(tb_str)
                raise ex
        