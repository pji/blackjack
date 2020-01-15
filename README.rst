=========
blackjack
=========

Yet another Python implementation of blackjack. The main purpose of 
this is to play around with basic concepts.


To Run
------
If you clone the repository, you can run it. Right now, all that it 
does is show a game between automated players, but if you want to 
see that, you can.

To see a game that is only the dealer, run the following from the root 
of your local copy of the repository::

    python3 -m blackjack.cli -d

To see a game that is the dealer and one player::

    python3 -m blackjack.cli -1

To see a game that is the dealer and two players::

    python3 -m blackjack.cli -2

To construct a game with four computer players, you as the fifth 
player, the initial bet set to 100, and all players starting with 
100 chips::

    python3 -m blackjack.cli -p 4 -u -c 100 -C 100

If you want to watch games between a dealer and four random players in 
the new curses-based UI::

    python3 -m blackjack.cli -D


Still To Do
-----------
The primary to-do list is complete.

The following features are on the nice-to-have list:

* Save game state.
* Restore game state.
* Add optional card count to display.
* Add will_*_never functions.
* Add will_*_random functions.
* Add random computer players joining and leaving game.
* Add card counting computer players.
* Add casino catching and removing card counting players.
* Allow splitting more than once.


Testing
-------
To run the unit tests, pull the repository and run the following from 
the root of the repository::

    python3 -m unittest discover tests

