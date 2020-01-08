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


Still To Do
-----------
The following features are on the to-do list:

* Let the user control a player.
* Add UI that updates information in place rather than listing events.
* Create a kick-off script at root to ease starting the script
* Save game state.
* Restore game state.

The following features are on the nice-to-have list:

* Add optional card count to display.
* Add will_*_never functions.
* Add will_*_random functions.
* Add random computer player construction.
* Add random computer players joining and leaving game.
* Add card counting computer players.
* Add casino catching and removing card counting players.


Testing
-------
To run the unit tests, pull the repository and run the following from 
the root of the repository::

    python3 -m unittest discover tests

