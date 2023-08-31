"""
cli
~~~

The module contains the basic classes used by blackjack for handling
a command line interface.

:copyright: (c) 2020 by Paul J. Iutzi
:license: MIT, see LICENSE for more details.
"""
import argparse
import traceback as tb
from collections import namedtuple
from time import sleep
from typing import Any, Generator, Optional, Sequence, Union

from blackjack import cards, game, model, players, termui


# UI objects.
class LogUI(game.BaseUI):
    tmp = '{:<15} {:<15} {:<}'

    def __init__(self, is_interactive: bool = False) -> None:
        self.is_interactive = is_interactive

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

    def start(
            self,
            is_interactive: bool = True,
            splash_title: Optional[Sequence[str]] = None
    ) -> None:
        """Print the initial banners for the game.

        :param is_interactive: Whether the session is viewed by a
            player.
        :return: None.
        :rtype: NoneType
        """
        self.is_interactive = is_interactive
        if self.is_interactive:
            print()
            if splash_title:
                for line in splash_title:
                    print(line)
                print()
            print(self.tmp.format('Player', 'Action', 'Hand'))
            print('\u2500' * 50)

    # Update methods.
    def _update_bet(self, player: players.Player,
                    bet: int,
                    event: str) -> None:
        """Report that a hand has changed.

        :param player: The player who owns the hand.
        :param bet: The amount of the bet that changed.
        :param event: The specific event to report.
        :return: None.
        :rtype: NoneType
        """
        fmt = f'{bet} ({player.chips})'
        self._update_event(player, event, fmt)

    def _update_event(self, player: players.Player, event: str,
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

    def _update_hand(
        self,
        player: players.Player,
        hand:cards.Hand,
        event: str
    ) -> None:
        """Report that a hand has changed.

        :param player: The player who owns the hand.
        :param hand: The hand that changed.
        :param event: The specific event to report.
        :return: None.
        :rtype: NoneType
        """
        self._update_event(player, event, hand)

    def _update_status(self, label: str, value: str) -> None:
        """Report that the game status has changed.

        :param label: The status that has changed.
        :param value: The new value of the status.
        :return: None.
        :rtype: NoneType
        """
        print(self.tmp.format(label, '', value))

    def bet(self, player, bet):
        """Player places initial bet."""
        self._update_bet(player, bet, 'Bet.')

    def cleanup(self, splash_title: Optional[Sequence[str]] = None) -> None:
        """Clean up after the round ends."""
        self.end()
        self.start(splash_title=splash_title)

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

    def update_count(self, value):
        """Update the running card count in the UI."""
        self._update_status('Running count:', value)

    def wins(self, player, bet):
        """Player wins."""
        self._update_bet(player, bet, 'Wins.')

    def wins_split(self, player, bet):
        """Player wins on their split hand."""
        self.wins(player, bet)

    # Input methods.
    def _multichar_prompt(
        self,
        prompt: str,
        default: str = ''
    ) -> str:
        """Prompt the user for multiple characters."""
        msg = f'{prompt} > '
        resp = input(prompt)
        if not resp:
            resp = default
        return resp

    def _yesno_prompt(
        self,
        prompt: str,
        default: Union[str, bool] = True
    ) -> model.IsYes:
        """Prompt the user for a yes/no answer."""
        response = None
        fmt = '{} [yn] > '

        # Repeat the prompt until you get a valid response.
        while not response:
            untrusted: Union[str, bool] = input(fmt.format(prompt))

            # Allow the response to default to true. Saves typing when
            # playing.
            if not untrusted:
                untrusted = default

            # Determine if the input is valid.
            try:
                response = model.IsYes(untrusted)

            # If it's not valid, the ValueError will be caught,
            # response won't be set, so the prompt will be repeated.
            except (ValueError, AttributeError):
                print('Invalid input.')

        return response

    def bet_prompt(self, bet_min: int, bet_max: int) -> model.Bet:
        """Ask user for a bet.."""
        # Set up prompt for input.
        prompt = f'How much do you wish to bet? [{bet_min}-{bet_max}]'
        default = str(bet_min)
        response: Optional[model.Bet] = None

        # Prompt for input until a valid input is received.
        while response is None:
            untrusted = self._multichar_prompt(prompt, default)
            try:
                response = model.Bet(untrusted, bet_max, bet_min)
            except ValueError:
                print('Invalid input.')

        # Validate and return.
        return response

    def doubledown_prompt(self) -> model.IsYes:
        """Ask user if they want to double down."""
        return self._yesno_prompt('Double down?', 'y')

    def hit_prompt(self) -> model.IsYes:
        """Ask user if they want to hit."""
        return self._yesno_prompt('Hit?', 'y')

    def insure_prompt(self, insure_max: int) -> model.Bet:
        """Ask user how much they want to insure."""
        # Set up prompt for input.
        prompt = f'How much insurance do you want? [0–{insure_max}]'
        default = '0'
        response: Optional[model.Bet] = None

        # Prompt for input until a valid input is received.
        while response is None:
            untrusted = self._multichar_prompt(prompt, default)
            try:
                response = model.Bet(untrusted, insure_max, 0)
            except ValueError:
                print('Invalid input.')

        # Validate and return.
        return response

    def nextgame_prompt(self) -> model.IsYes:
        """Ask user if they want to play another round."""
        return self._yesno_prompt('Next game?', 'y')

    def split_prompt(self) -> model.IsYes:
        """Ask user if they want to split."""
        return self._yesno_prompt('Split?', 'y')


# Command line mainline.
def parse_cli() -> argparse.Namespace:
    """Parse the command line options used to invoke the game."""
    p = argparse.ArgumentParser(
        prog='blackjack',
        description='Yet another Python implementation of blackjack.'
    )
    p.add_argument(
        '-a', '--automated_players_only',
        help='All users will be computer players.',
        action='store_true',
    )
    p.add_argument(
        '-b', '--buyin',
        help='The buyin amount for each hand.',
        action='store',
        type=int,
        default=20
    )
    p.add_argument(
        '-c', '--chips',
        help='Number of starting chips for the user.',
        action='store',
        type=int,
        default=200
    )
    p.add_argument(
        '-C', '--cut_deck',
        help='Cut cards from bottom of the deck to make counting harder.',
        action='store_true',
    )
    p.add_argument(
        '-d', '--decks',
        help='Number of standard decks to build the deck from.',
        action='store',
        type=int,
        default=6
    )
    p.add_argument(
        '-f', '--file',
        help='Restore the save from the given file.',
        action='store',
        type=str
    )
    p.add_argument(
        '-K', '--count_cards',
        help='Display running count in the UI.',
        action='store_true'
    )
    p.add_argument(
        '-L', '--use_logui',
        help='Use logging interface rather than table.',
        action='store_true'
    )
    p.add_argument(
        '-p', '--players',
        help='Number of computer players.',
        action='store',
        type=int,
        default=4
    )
    p.add_argument(
        '-s', '--save_file',
        help='Set the name of the save file.',
        action='store',
        type=str,
        default='save.json'
    )
    return p.parse_args()


def build_game(args: argparse.Namespace) -> game.Engine:
    """Build the game from the given arguments."""
    # Restore from save file.
    if args.file:
        engine = game.Engine.load(args.file.lstrip())
        seats = 1 + len(engine.playerlist)
        engine.ui = termui.TableUI(seats=seats, show_status=args.count_cards)
        return engine

    # Create dealer and players.
    dealer = players.Dealer(name='Dealer')
    playerlist = [
        players.make_player(bet=args.buyin)
        for _ in range(args.players)
    ]
    if not args.automated_players_only:
        user = players.UserPlayer(name='You', chips=args.chips)
        playerlist.append(user)

    # Build the UI.
    if args.use_logui:
        ui: game.EngineUI = LogUI()
    else:
        seats = 1 + len(playerlist)
        ui = termui.TableUI(seats=seats, show_status=args.count_cards)

    # Build and return the game.
    return game.Engine(
        dealer=dealer,
        playerlist=playerlist,
        ui=ui,
        buyin=args.buyin,
        save_file=args.save_file.lstrip(),
        deck_size=args.decks,
        deck_cut=args.cut_deck,
        running_count=args.count_cards
    )


def main() -> None:
    # Build the game.
    args = parse_cli()
    engine = build_game(args)

    # Play the game.
    try:
        loop = game.main(engine)
        play = next(loop)
        while play:
            play = loop.send(play)

    except Exception as ex:
        with open('exception.log', 'w') as fh:
            fh.write(str(ex.args))
            tb_str = ''.join(tb.format_tb(ex.__traceback__))
            fh.write(tb_str)
        engine.ui.end()
        raise ex


if __name__ == '__main__':
    main()
